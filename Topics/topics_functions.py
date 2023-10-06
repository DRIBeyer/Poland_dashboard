
import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from bertopic import BERTopic
from wordcloud import WordCloud, STOPWORDS


# Ensure you have these downloaded. Uncomment if necessary.
#nltk.download('stopwords')
#nltk.download('wordnet')

def clean_text(text):
    """
    Cleans the input text. Steps:
    - Convert to lowercase
    - Remove URLs
    - Remove punctuation
    - Remove numbers
    - Tokenize
    - Remove stopwords
    - Lemmatize
    """

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Tokenize
    tokens = text.split()

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word, pos='v') for word in tokens]

    # Return the cleaned text
    return ' '.join(tokens)

def process_dataframe(df):
    df["text_clean"] = df["translated_message"].apply(clean_text)
    return df
def filter_rows_by_terms(df, terms_list, column="message"):
    """
    Filter rows in a DataFrame based on whether the specified column contains any of the given terms.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - column (str): The column name in which to search for terms.
    - terms_list (list of str): List of terms to search for.

    Returns:
    - pd.DataFrame: Subset of the input DataFrame containing rows where the column has any of the terms.
    """

    def contains_term(text):
        if not isinstance(text, str):  # Check if text is a string
            return False

        # Check if the text contains any of the terms in terms_list
        for term in terms_list:
            if term.lower() in text.lower():
                return True

        return False

    mask = df[column].apply(contains_term)

    return df[mask].reset_index(drop=True)


def average_counts_by_title(df):
    """
    Calculate the average counts of 'likes', 'retweet/share', and 'reply/comment'
    broken down by values in the 'title' column.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.

    Returns:
    - pd.DataFrame: A DataFrame with 'title' values as rows and average counts as columns.
    """

    # Group by 'title' and calculate the mean for the specified columns
    result = df.groupby('title')[['likes', 'retweet/share', 'reply/comment']].mean().reset_index()

    return result


def clean_timestamps(column):
    """
    Cleans a list of timestamp strings to only include year, month, and day.

    Args:
    - column (list of str): The list of timestamp strings.

    Returns:
    - list of str: List with cleaned date strings.
    """
    pattern = r"(\d{4}-\d{2}-\d{2})(?:(?:\s\d{2}:\d{2}:\d{2})|(?:T\d{2}:\d{2}:\d{2}\.000Z))?"

    cleaned_data = []
    for date_str in column:
        match = re.match(pattern, date_str)
        if match:
            cleaned_data.append(match.group(1))
        else:
            cleaned_data.append(None)  # or you could append the original date_str if you prefer

    return cleaned_data


def count_posts_by_topic_per_day(df, Topics, filter_rows_by_terms):
    # Convert the 'date' column to datetime

    df["date"] = clean_timestamps(df.date)

    df['date'] = pd.to_datetime(df['date'])

    # Extract just the date component for our use
    df['date_only'] = df['date'].dt.date

    # Create a dataframe with unique dates (as native Python date objects)
    date_range = pd.DataFrame({'date': pd.date_range(start=df['date'].min().date(), end=df['date'].max().date()).date})

    # Iterate over each topic and its terms
    for topic, terms in Topics.items():

        # Filter the DataFrame using the terms
        topic_df = filter_rows_by_terms(df, terms)

        # Count the posts by day for the current topic
        daily_counts = topic_df.groupby('date_only').size().reset_index(name=topic)
        #print(date_range, daily_counts)
        # Merge the counts with the date_range to ensure all dates are present
        date_range = pd.merge(date_range, daily_counts, left_on='date', right_on='date_only', how='outer')
        date_range = date_range.drop(columns='date_only')
        #date_range = pd.merge(date_range, daily_counts, on=[['date', 'date_only']], how='outer',
         #                     suffixes=('_left', '_right'))

        # Forward-fill NaN values (to handle days with no posts)
        date_range[topic] = date_range[topic].fillna(0).astype(int)

    # Add a formatted date column
    date_range['time'] = date_range['date'].apply(lambda x: x.strftime('%d %B').replace(' 0', ' '))

    # Drop the original date column and reorder columns
    cols = ['time'] + list(Topics.keys())
    date_range = date_range[cols]

    return date_range

def sentiment_by_group(df):
    # Convert continuous sentiment scores to categorical values
    df['sentiment'] = pd.cut(df['sent_code'],
                             bins=[float('-inf'), -0.01, 0.01, float('inf')],
                             labels=['negative', 'neutral', 'positive'])

    # Group by title and sentiment, then count
    grouped = df.groupby(['title', 'sentiment']).size().reset_index(name='count')

    # Calculate percentages for each group (title)
    total_by_group = grouped.groupby('title')['count'].transform('sum')
    grouped['percentage'] = (grouped['count'] / total_by_group) * 100

    # Pivot to reformat the DataFrame
    result_df = grouped.pivot(index='sentiment', columns='title', values='percentage')

    return result_df.reset_index()

def extract_topics(df):
    # Create a BERTopic model with adjustments for small datasets
    model = BERTopic(nr_topics=5,  # target number of topics
                     language="english",
                     calculate_probabilities=True,
                     min_topic_size=2)  # adjust based on dataset size

    topics, _ = model.fit_transform(df['text_clean'])
    df['topic'] = topics

    # Check if only -1 (outlier topic) is detected
    if set(topics) == {-1}:
        topic_terms = pd.DataFrame({
            'Topic Label': [f"Topic {i}" for i in range(1, 6)],
            'Terms': ["No coherent topic detected"] * 5
        })
        return topic_terms

    # Get topic frequencies
    topic_freq = model.get_topic_freq()

    # Remove topic -1 (outlier topic)
    topic_freq = topic_freq[topic_freq['Topic'] != -1]

    # If more than 5 topics, retain only top 5 based on frequency
    if len(topic_freq) > 5:
        topic_freq = topic_freq.head(5)

    # Get topic terms and convert to DataFrame
    topic_dict = model.get_topics()
    topic_terms_df = pd.DataFrame(list(topic_dict.items()), columns=['Topic', 'Words'])

    # Merge the two DataFrames
    topic_terms = topic_freq.merge(topic_terms_df, left_on='Topic', right_on='Topic')

    # Rename columns for clarity
    topic_terms.rename(columns={'Count': 'Topic Frequency'}, inplace=True)

    # Format the topics to the desired "Topic X" format
    topic_terms['Topic Label'] = topic_terms['Topic'].apply(lambda x: f"Topic {x+1}")

    # Extract terms associated with each topic
    topic_terms['Terms'] = topic_terms['Words'].apply(lambda x: ', '.join([word[0] for word in x]))

    # Drop unnecessary columns and reset index
    topic_terms = topic_terms[['Topic Label', 'Terms']].reset_index(drop=True)

    return topic_terms.sort_values("Topic Label")


def clean_text(text):
    """
    Cleans the input text. Steps:
    - Convert to lowercase
    - Remove URLs
    - Remove punctuation
    - Remove numbers
    - Tokenize
    - Remove stopwords
    - Lemmatize
    """

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Tokenize
    tokens = text.split()

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word, pos='v') for word in tokens]

    # Return the cleaned text
    return ' '.join(tokens)

def process_dataframe(df):
    df["text_clean"] = df["translated_message"].apply(clean_text)
    return df


def create_wordcloud(df, column_name='text_clean'):
    """
    Generates a word cloud based on the specified text column of the dataframe and
    returns a DataFrame with words and their weights.

    Parameters:
    - df: DataFrame containing the text data.
    - column_name: Name of the column with text data. Default is 'text_clean'.

    Returns:
    - word_weights_df: DataFrame with words and their corresponding weights.
    """
    df = process_dataframe(df)
    # Combine all texts in the column into a single string
    combined_text = ' '.join(df[column_name].dropna())

    # Define additional stopwords if necessary
    stopwords = set(STOPWORDS)
    # e.g., stopwords.update(["word1", "word2"])

    # Set up the word cloud parameters
    wordcloud = WordCloud(stopwords=stopwords,
                          background_color='white',
                          width=800,
                          height=400,
                          max_words=200,
                          colormap='viridis',
                          contour_width=2,
                          contour_color='blue').generate(combined_text)

    # Convert word frequencies to DataFrame
    word_weights_df = pd.DataFrame(list(wordcloud.words_.items()), columns=['Word', 'Weight'])
    return word_weights_df