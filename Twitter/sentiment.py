# Import the necessary libraries
import spacy
from transformers import pipeline
import nltk
# Download the 'punkt' package, which is a NLTK pre-trained tokenizer for English
nltk.download('punkt')
# Import sentence tokenization function
from nltk.tokenize import sent_tokenize
# Importing functions from a local file 'drive_functions'
from drive_functions import *
from datetime import date, timedelta

# Get the current date
current_date = date.today()
print(current_date)

# Define the path to the data file using the current date
input_path = f".//Data//data_{current_date}.xlsx"
output_path = f".//Data//data_{current_date}.xlsx"
# Specify the ID of the Google Drive folder where the files are stored
google_drive_folder = "1XQzVMy7k_mTrVSXduyaoRNmgtdGj3Bmj"

# Read the excel file into a pandas DataFrame
df = pd.read_excel(input_path)

# Load the Polish spacy model for language processing tasks
nlp = spacy.load('pl_core_news_sm')

# Define the transformer model for text classification
model_path = "citizenlab/twitter-xlm-roberta-base-sentiment-finetunned"
sentiment_model = pipeline("text-classification", model=model_path, tokenizer=model_path)

# Define a function to preprocess the text
def preprocess_text(text):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Lowercase, lemmatize and remove stop words from each sentence
    preprocessed_sentences = []
    for sentence in sentences:
        doc = nlp(sentence.lower())
        preprocessed_sentence = ' '.join([token.lemma_ for token in doc if not token.is_stop])
        preprocessed_sentences.append(preprocessed_sentence)

    return preprocessed_sentences

# Define a function for sentiment analysis
def sentiment_analysis(preprocessed_sentences):
    # Get sentiment scores for each sentence
    sentiment = [sentiment_model(sentence)[0] for sentence in preprocessed_sentences]

    # Extract and adjust scores based on the sentiment label
    scores = []
    for res in sentiment:
        score = res['score']
        label = res['label'].lower()

        if label == 'negative':
            score *= -1
        elif label == 'neutral':
            score = 0

        scores.append(score)

    # Compute the overall sentiment score
    overall_score = sum(scores) / len(scores)

    return overall_score

# Define a function to print all positive sentences
def print_positive_sentences(preprocessed_sentences, labels):
    pos=[label=="positive" for label in labels]
    positive_sentences = [sentence for sentence, is_positive in zip(preprocessed_sentences, pos) if is_positive]
    for sentence in positive_sentences:
        print(sentence)

# Define a function to count the number of each sentiment
def count_sentiment(labels):
    positive_count = sum([label=="positive" for label in labels])
    negative_count = sum([label=="negative" for label in labels])
    neutral_count = sum([label=="neutral" for label in labels])

    return positive_count, negative_count, neutral_count

# Define a function to clean and analyze sentiment of a text
def clean_sent(text):
  preprocessed_s=preprocess_text(text)
  score=sentiment_analysis(preprocessed_s)
  return score

# Apply the 'clean_sent' function to the 'message' column and save the result in the 'sent_code' column
df["sent_code"] = df["message"].astype(str).apply(clean_sent)

# Save the DataFrame to an Excel file
df.to_excel(output_path)

# Convert all columns of the DataFrame to string type
df = df.astype("str")

# Save the DataFrame to Google Drive
save_dataframe_to_drive(df, f"data_{current_date}.xlsx", google_drive_folder)
