import requests
import pandas as pd
import time
import datetime
import os
from drive_functions import *

# Check whether folder Data exists and otherwise create it
folder_name = "Data"
google_drive_folder = "1x53Whuu7dZxB28wx_TZ67NiV2BlbbA27"

# Check if the data folder exists
if not os.path.exists(folder_name):
    # If not, create the data folder
    os.makedirs(folder_name)
    print(f"Folder '{folder_name}' created successfully.")
else:
    print(f"Folder '{folder_name}' already exists.")

# Get the current date and time
today = datetime.datetime.now()

# Subtract one week from today's date
one_week_ago = today - datetime.timedelta(days=8)
two_week_ago = today - datetime.timedelta(days=15)

# Convert today's date and one week ago to string format
today_str = today.strftime('%Y-%m-%d')
one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')
two_week_ago_str = two_week_ago.strftime('%Y-%m-%d')

# Define the path for saving the output file
output_path=f".//Data//data_{today_str}.xlsx"

# Define the token for authentication
token="R6xlcruOZi7ymsEZ1qsi1l9mNOV1LrXvK3cLp9J7"

# Define the function for getting posts via CrowdTangle API
def ct_get_posts(count=100, accounts=None, start_date=None, end_date=None, include_history=None,
                 sort_by="date", types=None, search_term=None, language=None,
                 min_interactions=0, offset=0, api_token=None):
    """
    This function retrieves data by CrowdTangle API.
    """

    # api-endpoint
    URL_BASE = "https://api.crowdtangle.com/posts"

    # Define parameters for the API request
    PARAMS = {'count': count, 'sortBy': sort_by, 'token': api_token,
              'minInteractions': min_interactions, 'offset': offset}

    # Add optional parameters if they are provided
    if accounts:
        PARAMS["accounts"] = ",".join(accounts)
    if start_date:
        PARAMS['startDate'] = start_date
    if end_date:
        PARAMS['endDate'] = end_date
    if include_history == 'true':
        PARAMS['includeHistory'] = include_history
    if types:
        PARAMS['types'] = types
    if search_term:
        PARAMS['searchTerm'] = search_term
    if language:
        PARAMS['language'] = language

    # Send a get request to the CrowdTangle API
    data = pd.DataFrame()
    next_page = ""
    count = 0

    while next_page or (count == 0):

        if PARAMS:
            r = requests.get(url=URL_BASE, params=PARAMS)
        else:
            r = requests.get(url=URL_BASE)

        time.sleep(10)
        count += 1
        print(count)
        if r.status_code != 200:
            out = r.json()
            print(f"status: {out['status']}")
            print(f"Code error: {out['code']}")
            print(f"Message: {out['message']}")
        else:
            res_data = r.json()
            pagination = res_data['result']['pagination']

            if 'nextPage' in pagination.keys():
                next_page = pagination['nextPage']
                URL_BASE = next_page
                PARAMS = {}
            else:
                next_page = ""
            df = pd.DataFrame(res_data['result']['posts'])
            data = pd.concat([data, df], axis=0)

    return data.reset_index(drop=True)

# Define the function for normalizing the data
def normalize_data(data):
    """
    This function converts columns "account" and "statistics", which are a series of dictionaries,
    into multiple columns and concatenates them to the initial dataset.
    """

    data = pd.concat([pd.json_normalize(data.account), data], axis=1)
    data = pd.concat([data, pd.json_normalize(data.statistics)], axis=1)
    data = data.drop(["account", "statistics"], axis=1)
    return data

# Define the function for data collection
def collect(excel_file):
    # Load Excel file
    xls = pd.ExcelFile(excel_file)

    # Get the names of all sheets in the Excel file
    sheet_names = xls.sheet_names

    # Sheets to be skipped
    skip_sheets = ['Media Institutions', 'NGO-CS', 'Clergy']

    # List to store dataframes
    dfs = []

    for sheet in sheet_names:
        # Skip the sheet if its name is in skip_sheets list
        if sheet in skip_sheets:
            continue

        df = pd.read_excel(xls, sheet_name=sheet)

        # Check if 'Facebook user' column exists
        if 'Facebook user' in df.columns:
            df['Facebook user'] = df['Facebook user'].str.replace('"', '')
            df['Facebook user'] = df['Facebook user'].str.replace('“', '')
            df['Facebook user'] = df['Facebook user'].str.replace('”', '')

            pages = df['Facebook user'].to_list()
            filtered_list = [x for x in pages if x not in ["", '', "nan", None]]
            filtered_list = [str(x) for x in filtered_list]

            # Get posts from these pages
            data = ct_get_posts(accounts=filtered_list, start_date=two_week_ago_str, end_date=one_week_ago_str, api_token=token)

            # Normalize data and add 'title' column
            data = normalize_data(data)
            data['title'] = sheet
            data.to_excel(f".//temp//data_{sheet}.xlsx")


# Define the function for concatenating Excel files
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

# Use the function
collect("Party.xlsx")

# Concatenate the Excel files
data = concatenate_excel_files(".//temp")

# Filter out posts with word count less than 4
data['word_count'] = data['message'].apply(lambda x: len(str(x).split()))
data = data[data['word_count'] > 3]

# Save data to an Excel file
data.to_excel(output_path)

# Convert dataframe to string
data = data.astype(str)

# Save dataframe to Google Drive
save_dataframe_to_drive(data, f"data_{today_str}.xlsx", google_drive_folder)
