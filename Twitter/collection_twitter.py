# -*- coding: utf-8 -*-
"""Collection Twitter.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ODDkNug0G2eacFl-QlYCN4cx7cztmmkb
"""



import requests
import datetime
import time
import os
from drive_functions import *

# Check whether folder Data exists and otherwise create it
folder_name = "Data"
google_drive_folder = "1XQzVMy7k_mTrVSXduyaoRNmgtdGj3Bmj"



# Check if the data folder exists
if not os.path.exists(folder_name):
    # If not, create the data folder
    os.makedirs(folder_name)
    print(f"Folder '{folder_name}' created successfully.")
else:
    print(f"Folder '{folder_name}' already exists.")

# Get the current date and time
from datetime import datetime, timedelta, date
today = date.today()

# Define the path to the data file using the current date
input_path = f".//Data//data_{today}.xlsx"
output_path = f".//Data//data_{today}.xlsx"


BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAABS4pQEAAAAAj%2BjWBTRYvruy0frkEH7mZLfok6M%3DpT5YRi5bUDYOxO0amNLbW4ZzqRH6og1RRYxDS9K5Bcaa1wXF4Z'

headers = {
    'Authorization': f'Bearer {BEARER_TOKEN}',
    'User-Agent': 'v2TwitterAPIPython'
}

def get_user_id(screen_name):
    url = f"https://api.twitter.com/2/users/by/username/{screen_name}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error getting user ID: {response.status_code}, {response.text}")
    return response.json()['data']['id']


def get_tweets_by_screen_names(screen_names):
    # Setting the start_date to one week before the current date
    start_date = datetime.utcnow() - timedelta(days=1)

    all_tweets = []

    delay = 60  # Start with a 1-minute delay
    max_delay = 900  # Max 15-minute delay

    for screen_name in screen_names:
        user_id = get_user_id(screen_name)
        next_token = None
        while True:
            url = f"https://api.twitter.com/2/users/{user_id}/tweets?expansions=author_id&tweet.fields=text,public_metrics,created_at&max_results=100"
            if next_token:
                url += f"&pagination_token={next_token}"

            response = requests.get(url, headers=headers)

            if response.status_code == 429:  # Rate limit exceeded
                print(f"Rate limit exceeded. Waiting for {delay} seconds.")
                time.sleep(delay)
                delay = min(2 * delay, max_delay)  # Double the delay for next time, up to max_delay
                continue
            elif response.status_code != 200:
                raise Exception(f"Error getting tweets: {response.status_code}, {response.text}")

            tweets_data = response.json()['data']
            meta_data = response.json().get('meta', {})

            for tweet in tweets_data:
                tweet_date = datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if tweet_date < start_date:
                    continue
                    # Skip retweets
                if tweet['text'].startswith("RT "):
                    continue
                tweet_info = {
                    'name': screen_name,
                    'screenname': screen_name,
                    'text': tweet['text'],
                    'date': tweet['created_at'],
                    'retweets': tweet['public_metrics']['retweet_count'],
                    'replies': tweet['public_metrics']['reply_count'],
                    'likes': tweet['public_metrics']['like_count'],
                    'quotes': tweet['public_metrics']['quote_count']
                }
                all_tweets.append(tweet_info)

            next_token = meta_data.get('next_token', None)
            if not next_token or tweet_date < start_date:
                break

            # Reset delay after successful call
            delay = 60

    return pd.DataFrame(all_tweets)


def collect(excel_file):
    # Load Excel file
    xls = pd.ExcelFile(excel_file)

    # Get the names of all sheets in the Excel file
    sheet_names = xls.sheet_names

    # List to store dataframes
    dfs = []

    for sheet in sheet_names:
        if sheet != "Media Institutions":
            df = pd.read_excel(xls, sheet_name=sheet)

            # Check if 'Facebook user' column exists
            if 'Twitter user' in df.columns:

                pages = df['Twitter user'].to_list()
                filtered_list = [x for x in pages if x not in ["", '', "nan", None]]
                filtered_list = [str(x) for x in filtered_list]

                # Get posts from these pages
                data = get_tweets_by_screen_names(filtered_list)


                data['title'] = sheet
                data.to_excel(f".//temp//data_{sheet}.xlsx")

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
from datetime import datetime, timedelta, date
today = date.today()

# Define the path to the data file using the current date
input_path = f".//Data//data_{today}.xlsx"
output_path = f".//Data//data_{today}.xlsx"


collect("Poland_Dataset.xlsx")


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