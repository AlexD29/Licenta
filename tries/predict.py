import torch
from transformers import BertTokenizer, BertForSequenceClassification

device = "cpu"
print(device)

# BERT setup
PRE_TRAINED_MODEL_NAME = 'dumitrescustefan/bert-base-romanian-cased-v1'
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(PRE_TRAINED_MODEL_NAME, num_labels=3).to(device)

# Load the fine-tuned model state
model.load_state_dict(torch.load('best_model_state.bin', map_location=device))

# Mapping from model output indices to labels
label_mapping = {
    0: "Positive",
    1: "Negative",
    2: "Neutral"
}

def predict_label(text, tokenizer, model):
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=100,
        truncation=True,
        padding='max_length',
        return_tensors='pt',
        return_attention_mask=True,
        return_token_type_ids=False,
    )

    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
        _, preds = torch.max(outputs.logits, dim=1)
        prediction = preds.cpu().item()
    
    return label_mapping[prediction]

# # Example usage:
# if __name__ == "__main__":
#     text = "Scandal in Parlament"
#     print(predict_label(text, tokenizer, model))
