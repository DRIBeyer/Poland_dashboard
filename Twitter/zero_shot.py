
# Import necessary libraries and modules
import re
import numpy as np
import pandas as pd
from collections import Counter
from transformers import pipeline
from drive_functions import *
from datetime import date, timedelta

# Get the current date
current_date = date.today()

# Define a list of selected topics
selection = ['Economy', 'External Relations', 'Social Groups', 'Freedom and Democracy']

# Define a dictionary containing themes and their associated subtopics
themes = {'Economy' : [
    "GDP",
    "Inflation",
    "Unemployment",
    "Exports",
    "Imports",
    "Industries",
    "Agriculture",
    "Tourism",
    "Investments",
    "Currency",
    "Debt",
    "Trade",
    "Manufacturing",
    "Infrastructure",
    "EU-Funds",
    "Energy",
    "FDI",
    "Technology",
    "Education",
    "Pensions"
],
'External Relations'  :  [
    "Security",
    "War",
    "Alliances",
    "Europe",
    "NATO",
    "Russia",
    "Energy",
    "Border",
    "Solidarity",
    "Trade",
    "Diplomacy",
    "EasternNeighbours",
    "Cybersecurity",
    "Migration",
    "V4",  # Visegrad Group
    "HumanRights",
    "Multilateralism",
    "BalticSea",
    "Defense",
    "Geopolitics",
    "Ukraine",
    "USA",
    "Germany",
    "France",
    "UK",
    "Belarus"
],
'Freedom and Democracy' : [
    "Democracy",
    "Constitution",
    "Elections",
    "Parliament",
    "Government",
    "President",
    "Parties",
    "PiS",  # Major political party in Poland
    "CivicPlatform",  # Major political party in Poland
    "Coalition",
    "Opposition",
    "Reforms",
    "Judiciary",
    "HumanRights",
    "Media",
    "EU",  # Poland's relationship with the EU
    "ForeignPolicy",
    "Defense",
    "Nationalism",
    "Immigration"
],
'Social Groups' : [
    "Youth",
    "Elderly",
    "Women",
    "Men",
    "LGBTQ+",
    "Immigrants",
    "Roma",
    "Students",
    "Workers",
    "Farmers",
    "Veterans",
    "Disabled",
    "ReligiousG",
    "Minorities",
    "Refugees",
    "Unemployed",
    "Rural",
    "Urban",
    "Educators",
    "Healthcare"
]
}

# Create input and output file paths using the current date
input_path = f".//Data//data_{current_date}.xlsx"
output_path = f".//Data//data_{current_date}.xlsx"

# Google Drive folder to save the data
google_drive_folder = "1XQzVMy7k_mTrVSXduyaoRNmgtdGj3Bmj"


# Function to clear the screen, works for both Windows and Unix-based systems
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Read data from the input Excel file into a pandas DataFrame
#input_path="Data/data_2023-07-29.xlsx"
df = pd.read_excel(input_path)


# Function to remove hashtags from a sentence using regular expressions
def remove_hashtags(sentence):
    return re.sub(r'#\w+', '', sentence)


# Function to filter labels and scores based on a standard deviation threshold
def filter_labels_scores(row):
    labels = row['labels']
    scores = row['scores']
    std_dev = np.std(scores)
    labels_filtered = [label for label, score in zip(labels, scores) if score > 2 * std_dev]
    scores_filtered = [score for score in scores if score > 2 * std_dev]
    if len(labels_filtered) > 3:
        labels_filtered = np.nan
        scores_filtered = np.nan
    else:
        labels_filtered = labels_filtered
        scores_filtered = scores_filtered
    return pd.Series({'labels': labels_filtered, 'scores': scores_filtered})


# Function to get the label distribution for a specific topic
def get_label_distribution(df, topic_label, candidate_labels):
    # Filter the DataFrame to include only rows with the specified topic label
    df_filtered = df[df["topic_label"] == topic_label]

    # Extract and preprocess the review messages (remove hashtags)
    sequences = df_filtered['translated_message'].apply(remove_hashtags).to_list()

    # Instantiate the zero-shot classifier
    classifier = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli", device=-1)

    # Set the hypothesis template for classification
    hypothesis_template = "The topic of this review is {}."

    # Perform zero-shot classification on the review messages
    single_topic_prediction = classifier(sequences, candidate_labels, hypothesis_template=hypothesis_template)

    # Convert the results into a DataFrame and filter labels and scores
    single_topic_prediction = pd.DataFrame(single_topic_prediction)
    single_topic_prediction[['labels', 'scores']] = single_topic_prediction.apply(filter_labels_scores, axis=1)

    # Convert the 'labels' column to a list, removing all missing values
    labels_list = single_topic_prediction['labels'].dropna().tolist()

    # Flatten the list of labels
    flat_labels_list = [item for sublist in labels_list for item in sublist]

    # Count occurrences of each label
    label_counter = Counter(flat_labels_list)

    # Convert label counts to percentages
    total = sum(label_counter.values(), 0.0)
    for key in label_counter:
        label_counter[key] = round((label_counter[key] / total) * 100,
                                   2)  # Calculate percentage and round to 2 decimal places

    # Convert the label counts into a DataFrame and sort by percentage in descending order
    label_counter_df = pd.DataFrame(list(label_counter.items()), columns=['Label', topic_label])
    return label_counter_df.sort_values(topic_label, ascending=False)


# Add a new column 'word_count' to the DataFrame, representing the word count of each review message
df['word_count'] = df['translated_message'].apply(lambda x: len(str(x).split()))

# Filter the DataFrame to include only rows with a word count greater than 3
df_filtered = df[df['word_count'] > 3]

# Iterate through the selected topics and get their label distribution, saving results in Google Sheets
for item in selection:
    topic_label = item
    candidate_labels = themes[item]
    counts = get_label_distribution(df_filtered, topic_label, candidate_labels)

    # Limit the results to the top 10 labels if there are more than 10
    if len(counts) > 10:
        counts = counts.head(10)

    # Save the DataFrame into a Google Sheets tab with the corresponding topic label
    spreadsheet = "1X1414Avpr8YfwF5htSEo5YXHzsVlkhmoInhWzlyXTds"
    spreadsheet_name = item
    save_dataframe_in_tab(counts, spreadsheet, spreadsheet_name)
