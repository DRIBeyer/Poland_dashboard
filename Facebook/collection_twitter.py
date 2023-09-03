# Import necessary libraries
import pandas as pd
from twitter_functions import *
from datetime import date, timedelta
import tweepy
import json
from datetime import date, timedelta
import pandas as pd
# Open and read the credentials.json file
with open('credentials.json') as file:
    data = json.load(file)

# Get the current date
current_date = date.today()
print(current_date)

# Calculate the date one week ago from the current date
one_week_ago = current_date - timedelta(weeks=1)

# Transform the date into a string and then into a list of integers
start_date=str(one_week_ago).split("-")
start_date=[int(x) for x in start_date]

# Get the bearer token from the loaded data
bearer_token=data['bearer_token']

# Get the current working directory
current_path = os.getcwd()

# List of screen names
screen_names=["JKaczyski", "FilipKaczynski", "gazeta_wyborcza"]

# For each screen name, get the user's timeline
for screen_name in screen_names:
    get_users_timeline(bearer_token=bearer_token,date_from=start_date, screen_name=screen_name)

# Directory path where the timelines are stored
directory=f".//users_timeline//{current_date}"

# Initialize a list to store DataFrame objects
df_list = []

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a JSON file
    if filename.endswith("tweets.json"):
        # Construct the full file path
        filepath = os.path.join(directory, filename)
        # Open the JSON file and load its data
        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
            # Create a DataFrame from the loaded data and append it to the list
            df=pd.DataFrame(data)
            df_list.append(df)
user_df=[]
# Loop through all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a JSON file
    if filename.endswith("users.json"):
        # Construct the full file path
        filepath = os.path.join(directory, filename)
        # Open the JSON file and load its data
        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
            # Create a DataFrame from the loaded data and append it to the list
            df=pd.DataFrame(data)
            user_df.append(df)

# Get the path to the current file and the directory it's in
current_file_path = os.path.realpath(__file__)
current_directory = os.path.dirname(current_file_path)

# Define the final directory path
final_directory = f"{current_directory}//data//{current_date}"

# If the final directory does not exist, create it
if not os.path.exists(final_directory):
    os.makedirs(final_directory)

# Concatenate all DataFrames in the list into a single DataFrame
df = pd.concat(df_list)
print(df.author_id.unique())
df_names = pd.concat(user_df)
print(df_names.id.unique())
df_final=pd.merge(df, df_names, left_on="author_id", right_on="id")
df_final.to_excel(f"{final_directory}//data.xlsx")

#
#
# with open('credentials.json') as file:
#     data = json.load(file)
#
# consumer_key = data['api_key']
# bearer_token =  data['bearer_token']
# access_token = data['access_token']
# access_token_secret = data['access_token_secret']
#
# client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, access_token=access_token, access_token_secret=access_token_secret)
#
#
# names={}
# author_ids = df.author_id.unique().tolist()
# for id in author_ids:
#     try:
#         users = client.get_user(id=id)
#         name=users[0]
#         name = name
#         print(name)
#         names[id]=name
#     except:
#         continue
#
# s=df["author_id"]
# s = [names[x] for x in s]
# df["full_name"]=s
#
#
# # Write the final DataFrame to an Excel file in the final directory
# df.to_excel(f"{final_directory}//data.xlsx")
