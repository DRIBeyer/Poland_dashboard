from drive_functions import *
from transformers import pipeline
from datetime import date, timedelta
# Get today's date

current_date = date.today()

input_path = f".//Data//data_{current_date}.xlsx"
output_path = f".//Data//data_{current_date}.xlsx"
google_drive_folder = "1x53Whuu7dZxB28wx_TZ67NiV2BlbbA27"


#df = pd.read_excel("Data/data_2023-07-29.xlsx")
df = pd.read_excel(input_path)

def emo_predict(text):
    classifier = pipeline("text-classification", model='bhadresh-savani/roberta-base-emotion', return_all_scores=False)
    prediction = classifier(text)
    prediction_label = prediction[0]
    return prediction_label["label"]

def df_emo_predict(df):
    df["emotion"] = df.apply(
        lambda row: emo_predict(row["translated_message"]) if row["sent_code"] > 0.1 or row["sent_code"] < -0.1 else "neutral",
        axis=1
    )
    return df

df_new = df_emo_predict(df)
df_new.to_excel(output_path)

df_new = df_new.astype("str")

save_dataframe_to_drive(df_new, f"data_{current_date}.xlsx", google_drive_folder)