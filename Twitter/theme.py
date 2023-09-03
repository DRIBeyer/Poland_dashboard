# Import necessary libraries
import swifter
from drive_functions import *
import pandas as pd
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch
import joblib



from datetime import date, timedelta

# Get the current date
current_date = date.today()

# Define the path to the data file using the current date
input_path = f".//Data//data_{current_date}.xlsx"
output_path = f".//Data//data_{current_date}.xlsx"
google_drive_folder = "1XQzVMy7k_mTrVSXduyaoRNmgtdGj3Bmj"

# Load the Excel file into a DataFrame

df = pd.read_excel(input_path)
#df = pd.read_excel(".//Data//data_2023-09-01.xlsx")
# Load pre-trained RoBERTa model for sequence classification
model_path = "Model/roberta_model"
model = RobertaForSequenceClassification.from_pretrained(model_path)

# Load pre-trained RoBERTa tokenizer
tokenizer_path = "Model/roberta_tokenizer"
tokenizer = RobertaTokenizer.from_pretrained(tokenizer_path)

# Load label encoder model
le_path = 'Model/label_encoder.joblib'
le = joblib.load(le_path)

# If CUDA is available, move the model to GPU for faster computation
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model.to(device)

# Function for prediction
def predict(text, model=model, tokenizer=tokenizer):
    # Tokenize the text and get it ready for the model
    encoded_text = tokenizer.encode_plus(
        text,
        truncation=True,
        add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
        return_token_type_ids=False,
        padding='max_length',
        max_length=512,  # Max length to truncate/pad
        return_attention_mask=True,  # Construct attention masks
        return_tensors='pt',  # Return pytorch tensors
    )

    # Move tensors to the device where the model is
    input_ids = encoded_text['input_ids'].to(device)
    attention_mask = encoded_text['attention_mask'].to(device)

    # Get the model's predictions
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)

    # Determine the class with the highest prediction score
    predicted_class_idx = torch.argmax(outputs.logits, dim=-1).item()

    # Convert class ID back to label name using the label encoder
    predicted_class_label = le.inverse_transform([predicted_class_idx])[0]

    # Convert the labels to a more human readable format
    if predicted_class_label == 1:
        return_label = "External Relations"
    elif predicted_class_label == 2:
        return_label = "Freedom and Democracy"
    elif predicted_class_label == 3:
        return_label = "Political System"
    elif predicted_class_label == 4:
        return_label = "Economy"
    elif predicted_class_label == 5:
        return_label = "Welfare and Quality of Life"
    elif predicted_class_label == 6:
        return_label = "Fabric of Society"
    elif predicted_class_label == 7:
        return_label = "Social Groups"
    elif predicted_class_label == 8:
        return_label = "None"
    else:
        return_label = "Invalid label"

    # Return the label
    return return_label

# Apply the prediction function to all messages in the DataFrame
df["topic_label"] = df["translated_message"].astype(str).swifter.apply(predict)

# Save the DataFrame with predictions to an Excel file
df.to_excel(output_path)

# Convert all values in the DataFrame to strings
df = df.astype("str")

# Save the DataFrame to Google Drive
save_dataframe_to_drive(df, f"data_{current_date}.xlsx", google_drive_folder)
