def concatenate_excel_files(directory):
    # Initialize an empty dataframe
    all_data = pd.DataFrame()

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is an Excel file
            if file.endswith(".xlsx") or file.endswith(".xls"):
                # Construct the full file path
                file_path = os.path.join(root, file)

                # Load the Excel file
                df = pd.read_excel(file_path)

                # Concatenate the data
                all_data = pd.concat([all_data, df], ignore_index=True)

    return all_data


import pandas as pd


def find_twitter_users(excel_file_path):
    # Initialize an empty dictionary to store the results
    twitter_users = {}

    # Load Excel file
    xls = pd.ExcelFile(excel_file_path)

    # Loop through each sheet in the Excel file
    for sheet_name in xls.sheet_names:
        # Read the sheet into a DataFrame
        df = pd.read_excel(xls, sheet_name)
        print(sheet_name)
        # Check if both "Twitter user" and "Name" columns exist in the DataFrame
        if 'Twitter user' in df.columns and 'Name' in df.columns:
            # Loop through each row in the DataFrame
            for index, row in df.iterrows():
                twitter_user = row['Twitter user']
                name = row['Name']

                # Only add to dictionary if both fields are non-empty
                if pd.notna(twitter_user) and pd.notna(name):
                    twitter_users[twitter_user] = name

    return twitter_users


# Test the function with an Excel file
result = find_twitter_users("Poland_Dataset.xlsx")
print(result)

# Get the current date and time
import requests
import datetime
import time
import os
from drive_functions import *

# Check whether folder Data exists and otherwise create it
folder_name = "Data"
google_drive_folder = "1XQzVMy7k_mTrVSXduyaoRNmgtdGj3Bmj"
from datetime import datetime, timedelta, date
today = date.today()

# Define the path to the data file using the current date
input_path = f".//Data//data_{today}.xlsx"
output_path = f".//Data//data_{today}.xlsx"


#collect("Poland_Dataset.xlsx")


# Concatenate the Excel files
data = concatenate_excel_files(".//temp")

# Filter out posts with word count less than 4
data['word_count'] = data['text'].apply(lambda x: len(str(x).split()))
data = data[data['word_count'] > 3]
data["name"] = data["name"].replace(result)
data.dropna(subset=['name'], inplace=True)
data["message"]=data["text"]
# Save data to an Excel file
data.to_excel(output_path)

# Convert dataframe to string
data = data.astype(str)

# Save dataframe to Google Drive
save_dataframe_to_drive(data, f"data_{today}.xlsx", google_drive_folder)