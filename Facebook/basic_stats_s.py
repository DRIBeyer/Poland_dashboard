import pandas as pd
import os
from datetime import datetime
from openpyxl import load_workbook
today = datetime.today().strftime('%Y-%m-%d')

# Get the directory of the current script
current_script_directory = os.path.dirname(os.path.abspath(__file__))

## finding list of folders within a folder
def list_folders(directory):
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

# Specify the directory you want to list folders for
directory = f'{current_script_directory}\\Data\\Subsets'


#### do analysis for each of the subfolders
folders = list_folders(directory)
for folder in folders:
    file_path=f"{directory}\\{folder}\\{today}.xlsx"
    df=pd.read_excel(file_path)
    df["one"]=1

    posting_activity=df.groupby('name').agg({'one': 'sum', 'subscriberCount': 'mean'}).reset_index()
    # Perform the groupby operation with custom column names
    posting_activity = df.groupby('name').agg(
        Message_Sum=('one', 'sum'),
        SubscriberCount_Mean=('subscriberCount', 'mean')
    ).reset_index()

    import os

    ####create a folderpath for the basic analysis
    folder_path = f"{directory}\\{folder}\\basic_stats"
    ### check whether folder exists or otherwise create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Specify the path to the Excel file
    file_path = f"{folder_path}\\stats.xlsx"

    # Check if the file exists
    if not os.path.exists(file_path):
        # If the file does not exist, create an empty DataFrame
        df = pd.DataFrame()

        # Write the empty DataFrame to an Excel file
        df.to_excel(file_path)

    # Specify the name of the sheet you want to write to
    sheet_name = f"{today}_p_activity"  # replace with your sheet name

    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        posting_activity.to_excel(writer, sheet_name=sheet_name)

    ### remove empty Sheet1 in the beginning
    try:
        # Load the workbook
        wb = load_workbook(file_path)

        std = wb['Sheet1']

        # Remove the sheet
        wb.remove(std)
        # Save the workbook
        wb.save(file_path)
    except:
        continue