# Import necessary libraries
import pandas as pd
from datetime import datetime
import os

# Get the current date and format it as 'YYYY-MM-DD'
today = datetime.today().strftime('%Y-%m-%d')

# Read the Excel file named with today's date from the 'Data' directory
df = pd.read_excel(f"Data/{today}.xlsx")

# Remove any rows from the dataframe where the 'message' column is missing
df = df.dropna(subset=["message"])

# Define a dictionary of categories and associated words
# The script will create subsets of the dataframe for each category
# Each subset will include only rows where the 'message' contains any of the associated words
target_set = {
    "election": ["wybory", "głosowanie", "parlament", "sondy"],
    "party": ["członkowie", "lider", "prawo"],
}

# Loop over the categories in target_set
for set in target_set:
    # Define the name of the folder where the subset for the current category will be saved
    folder_name = f"Data/Subsets/{set}"

    # Check if the folder for the current category already exists
    if not os.path.exists(folder_name):
        # If the folder doesn't exist, create it
        os.makedirs(folder_name)
        print(f'Folder "{folder_name}" created.')
    else:
        print(f'Folder "{folder_name}" already exists.')

    df["message"]=df.message.str.lower()

    # Create a subset of the dataframe
    # Include only rows where the 'message' contains any of the words associated with the current category
    subset = df[df['message'].str.contains('|'.join(target_set[set]))]

    # Save the subset to an Excel file in the category's folder
    # The name of the file is the current date (in 'YYYY-MM-DD' format) with an '.xlsx' extension
    subset.to_excel(f"{folder_name}/{today}.xlsx")

