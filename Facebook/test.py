from drive_functions import *
from datetime import date, timedelta
import swifter
# Get the current date
current_date = date.today()

# Define the path to the data file using the current date
input_path=f".//Data//data_{current_date}.xlsx"
output_path=f".//Data//data_{current_date}.xlsx"
google_drive_folder = "1x53Whuu7dZxB28wx_TZ67NiV2BlbbA27"


df = pd.read_excel(".\\Data\\data_2023-09-25.xlsx")

specific_date = '2023-09-14'
df = df[df['date'] > specific_date]

df.to_excel(output_path)


df = df.astype(str)

save_dataframe_to_drive(df, f"data_{current_date}.xlsx", google_drive_folder)