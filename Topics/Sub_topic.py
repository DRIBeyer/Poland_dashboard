from drive_functions import *
from topic_lists import *
from topics_functions import *
from datetime import date, timedelta
current_date = date.today()


df1 = create_dataframe_from_folder("1XQzVMy7k_mTrVSXduyaoRNmgtdGj3Bmj")
df2 = create_dataframe_from_folder("1x53Whuu7dZxB28wx_TZ67NiV2BlbbA27")

mapping_dict = {
    'retweets':"retweet/share",
    'actual.shareCount':"retweet/share",
    'replies': "reply/comment",
    'actual.commentCount': "reply/comment",
    'likes':"likes",
    'actual.likeCount':"likes"
}
def rename_columns(df, mapping_dict = mapping_dict):
    """
    Rename columns in the DataFrame based on a mapping dictionary.

    Parameters:
    - df (pd.DataFrame): The DataFrame whose columns you want to rename.
    - mapping_dict (dict): A dictionary containing the current column names (keys) and the desired new names (values).

    Returns:
    - pd.DataFrame: The DataFrame with the renamed columns.
    """

    # Check if the columns in the dictionary keys exist in the DataFrame
    for old_name in mapping_dict.keys():
        if old_name not in df.columns:
            print(f"Warning: Column '{old_name}' does not exist in the DataFrame.")

    # Use the DataFrame's rename method to rename the columns
    return df.rename(columns=mapping_dict)


df1 = rename_columns(df1)
df2 = rename_columns(df2)


selection = ['date','message', 'translated_message', 'sent_code', 'emotion', 'toxicity',
       'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_attack',
       'topic_label', 'likes', 'retweet/share',
       'reply/comment']


def concatenate_dfs(df1, df2):
    """
    Concatenates two dataframes along the rows (i.e., vertically).

    Parameters:
    - df1: First DataFrame
    - df2: Second DataFrame

    Returns:
    - Concatenated DataFrame
    """
    return pd.concat([df1, df2], ignore_index=True)

df = concatenate_dfs(df1, df2)

df=df[df["title"] !="Clergy"]
df=df[df["title"] !="NGO-CS"]

df.to_excel(f"{current_date}_concatinated.xlsx")



######################################ANALYSIS###########################################################
folder_name="1Xsp3X-Re9PC5NBRCDwx5mnXzChczDQy0"

method = "topic_count"
topic_count = count_posts_by_topic_per_day(df, Topics, filter_rows_by_terms)

topic_count=topic_count.astype("str")

save_dataframe_to_drive(topic_count, f"{method}.xlsx", folder_name)


df = process_dataframe(df)

for T in Topics:

  subset = filter_rows_by_terms(df, Topics[T])

  topic = T

  method="reactions"

  reactions_df = average_counts_by_title(subset)
  reactions_df = reactions_df.astype("str")

  save_dataframe_to_drive(reactions_df, f"{topic}_{method}.xlsx", folder_name)

  method = "sentiment"

  sentiment_percentage = sentiment_by_group (subset)

  sentiment_percentage=sentiment_percentage.astype("str")

  save_dataframe_to_drive(sentiment_percentage, f"{topic}_{method}.xlsx", folder_name)

  method = "wordcloud"

  wordcloud = create_wordcloud(subset)
  wordcloud = wordcloud.astype("str")
  save_dataframe_to_drive(wordcloud, f"{topic}_{method}.xlsx", folder_name)



  try:
      method = "topic"
      topic_found = extract_topics(subset)
      topic_found = topic_found.astype("str")
      save_dataframe_to_drive(topic_found, f"{topic}_{method}.xlsx", folder_name)

  except:
      continue


