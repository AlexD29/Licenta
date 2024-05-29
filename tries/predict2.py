import pandas as pd
import torch
from transformers import BertForSequenceClassification, BertTokenizer
from torch.utils.data import Dataset, DataLoader

# Device setup
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

# BERT setup
PRE_TRAINED_MODEL_NAME = 'dumitrescustefan/bert-base-romanian-cased-v1'
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(PRE_TRAINED_MODEL_NAME).to(device)

# Load your new dataset
df_new = pd.read_csv('./tries/model.csv')


class CustomDataset(Dataset):
    def __init__(self, texts, tokenizer, max_len):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            truncation=True,
            padding='max_length',
            return_tensors='pt',
            return_attention_mask=True,
            return_token_type_ids=False,
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
        }


MAX_LEN = 100
new_dataset = CustomDataset(df_new['Content'].values, tokenizer, MAX_LEN)
new_data_loader = DataLoader(new_dataset, batch_size=32, shuffle=False)


def get_predictions(model, data_loader):
    model = model.eval()
    predictions = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)

            outputs = model(input_ids, attention_mask)
            _, preds = torch.max(outputs.logits, dim=1)

            predictions.extend(preds.cpu().numpy())

    return predictions


# Get predictions
predictions = get_predictions(model, new_data_loader)

class_names = ["Bucurie", "Furie", "Frica", "Tristete", "Neutru"]

# Mapping from original class names to new labels
label_mapping = {
    "Bucurie": "Positive",
    "Furie": "Negative",
    "Frica": "Negative",
    "Tristete": "Negative",
    "Neutru": "Neutral"
}

# Convert predictions to new labels
predicted_labels = [label_mapping[class_names[pred]] for pred in predictions]

# Add predicted labels to the DataFrame
df_new['Label'] = predicted_labels

# Save DataFrame back to CSV file with predictions
df_new.to_csv('./tries/model.csv', index=False, encoding='utf-8-sig')
