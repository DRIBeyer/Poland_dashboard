from drive_functions import *


df = pd.read_excel(".\\Data\\data_2023-08-28.xlsx")


def process_and_upload(df, mapping_dict):
    # Assuming there's a column named 'date' in your df. If not, replace 'date' with the appropriate column name
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%B')  # Extracting month name

    # List of names to be considered
    names_order = [
        'Donald Tusk',
        'Mateusz Morawiecki',
        'Paweł Kukiz',
        'Sławomir Mentzen',
        'Władysław Kosiniak-Kamysz',
        'Włodzimierz Czarzasty'
    ]

    # Rename the columns based on the mapping_dict
    df = df.rename(columns=mapping_dict)

    # Subset the DataFrame for rows with 'National Politicians' in the 'title' column and the given names
    df = df[(df['title'] == 'National Politicians') & (df['name'].isin(names_order))]

    # Create an empty dictionary to store the aggregated data for each group
    aggregated_data = {}

    # Count the number of posts for each group by month
    message_count = df.pivot_table(index='name', columns='month', aggfunc='size', fill_value=0).reset_index()
    aggregated_data['message count'] = message_count

    # Calculate averages for the renamed columns and store in the aggregated_data dictionary
    for original_col, renamed_col in mapping_dict.items():
        group_data = df.pivot_table(index='name', columns='month', values=renamed_col, aggfunc='mean',
                                    fill_value=0).reset_index()
        aggregated_data[renamed_col] = group_data

    # Use the previous function to upload each aggregated DataFrame to the specified Google Sheet
    spreadsheet_id = "1CA8UcL_ap5USX87-HPco6XgvQHDNjyz4h59ItuP7pTQ"
    for tab_name, data in aggregated_data.items():
        # Convert the entire DataFrame to string format to prevent JSON errors
        data = data.astype("str")
        save_dataframe_preserve_col_A(data, spreadsheet_id, tab_name)


mapping_dict = {
    'retweets':"retweet/share",
    'actual.shareCount':"retweet/share",
    'replies': "reply/comment",
    'actual.commentCount': "reply/comment",
    'likes':"likes",
    'actual.likeCount':"likes"
}

# Assuming df has already been defined or loaded
process_and_upload(df, mapping_dict)
