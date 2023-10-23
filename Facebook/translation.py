# Import necessary libraries
from datetime import date, timedelta
import pandas as pd
from transformers import MarianMTModel, MarianTokenizer
from drive_functions import *
import swifter
# Get the current date
current_date = date.today()

# Define the path to the data file using the current date
input_path=f".//Data//data_{current_date}.xlsx"
#input_path=f".//Data//data_2023-10-12.xlsx"
output_path=f".//Data//data_{current_date}.xlsx"
google_drive_folder = "1x53Whuu7dZxB28wx_TZ67NiV2BlbbA27"
# Load the data from the Excel file into a pandas DataFrame
df = pd.read_excel(input_path)

# Specify the name of the pre-trained model to use for translation
model_name = 'Helsinki-NLP/opus-mt-pl-en'

# Load the tokenizer and model for the specified pre-trained model
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)


# Define a function to translate text
def translate(text):
    # Tokenize the input text, preparing it for the model
    tokenized_text = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Use the model to generate a translation
    translation = model.generate(**tokenized_text, max_length=50, num_beams=5, early_stopping=True)

    # Decode the output from the model, converting it to readable text
    translated_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translation]

    # Return the translated text
    return translated_text[0]


## drop missing values
df = df.dropna(subset="message")

# Use the translate function to translate the 'text' column of the DataFrame
df['translated_message'] = df['message'].swifter.apply(translate)

# Save the DataFrame, including the translations, back to the Excel file
df.to_excel(output_path)


df = df.astype(str)

save_dataframe_to_drive(df, f"data_{current_date}.xlsx", google_drive_folder)
