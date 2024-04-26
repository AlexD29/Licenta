import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch import nn, optim
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import nltk
from transformers import BertTokenizer, BertModel

# Device setup
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

# Constants
EPOCHS = 5
BATCH_SIZE = 8
MAX_LEN = 100
class_names = ["Bucurie", "Furie", "Frica", "Tristete", "Neutru"]

df_train = pd.read_csv(r"../data/train_modified.csv")
df_val = pd.read_csv(r"../data/val_modified.csv")
df_test = pd.read_csv(r"../data/test_modified.csv")

# Preprocess datasets
label_encoder = LabelEncoder()

df_train.Emotion = label_encoder.fit_transform(df_train.Emotion)
df_val.Emotion = label_encoder.transform(df_val.Emotion)
df_test.Emotion = label_encoder.transform(df_test.Emotion)

# Create data loaders
class RED(Dataset):
    def __init__(self, texts, emotions, tokenizer, max_len):
        self.texts = texts
        self.emotions = emotions
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        emotion = self.emotions[item]

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'input_ids': inputs['input_ids'].flatten(),
            'attention_mask': inputs['attention_mask'].flatten(),
            'emotions': torch.tensor(emotion, dtype=torch.long)
        }

def create_data_loader(df, tokenizer, max_len, batch_size):
    ds = RED(
        texts=df.Content.to_numpy(),
        emotions=df.Emotion.to_numpy(),
        tokenizer=tokenizer,
        max_len=max_len
    )
    return DataLoader(
        ds,
        batch_size=batch_size,
        num_workers=0
    )

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

train_data_loader = create_data_loader(df_train, tokenizer, MAX_LEN, BATCH_SIZE)
val_data_loader = create_data_loader(df_val, tokenizer, MAX_LEN, BATCH_SIZE)
test_data_loader = create_data_loader(df_test, tokenizer, MAX_LEN, BATCH_SIZE)

# Model definition
class EmotionsClassifier(nn.Module):
    def __init__(self, n_classes):
        super(EmotionsClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.drop = nn.Dropout(p=0.3)
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=False
        )
        pooled_output = self.drop(pooled_output)
        output = self.out(pooled_output)
        return output

model = EmotionsClassifier(n_classes=len(class_names)).to(device)

# Training and Evaluation functions
def train_epoch(model, data_loader, loss_fn, optimizer, device, scheduler, n_examples):
    model = model.train()
    losses = []
    correct_predictions = 0

    for d in data_loader:
        input_ids = d["input_ids"].to(device)
        attention_mask = d["attention_mask"].to(device)
        emotions = d["emotions"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        _, preds = torch.max(outputs, dim=1)
        loss = loss_fn(outputs, emotions)
        correct_predictions += torch.sum(preds == emotions)
        losses.append(loss.item())
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

    return correct_predictions.double() / n_examples, np.mean(losses)

def eval_model(model, data_loader, loss_fn, device, n_examples):
    model = model.eval()
    losses = []
    correct_predictions = 0

    with torch.no_grad():
        for d in data_loader:
            input_ids = d["input_ids"].to(device)
            attention_mask = d["attention_mask"].to(device)
            emotions = d["emotions"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            _, preds = torch.max(outputs, dim=1)
            loss = loss_fn(outputs, emotions)
            correct_predictions += torch.sum(preds == emotions)
            losses.append(loss.item())

    return correct_predictions.double() / n_examples, np.mean(losses)

optimizer = optim.AdamW(model.parameters(), lr=2e-5)
total_steps = len(train_data_loader) * EPOCHS
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.1)

# Loss function
loss_fn = nn.CrossEntropyLoss().to(device)

# Training loop
history = defaultdict(list)
best_accuracy = 0

for epoch in range(EPOCHS):
    print(f'Epoch {epoch + 1}/{EPOCHS}')
    print('-' * 10)
    train_acc, train_loss = train_epoch(
        model,
        train_data_loader,
        loss_fn,
        optimizer,
        device,
        scheduler,
        len(df_train)
    )
    print(f'Training loss {train_loss} accuracy {train_acc}')

    val_acc, val_loss = eval_model(
        model,
        val_data_loader,
        loss_fn,
        device,
        len(df_val)
    )

    print(f'Validation loss {val_loss} accuracy {val_acc}')
    print()

    history['train_acc'].append(train_acc)
    history['train_loss'].append(train_loss)
    history['val_acc'].append(val_acc)
    history['val_loss'].append(val_loss)

    if val_acc > best_accuracy:
        torch.save(model.state_dict(), 'best_model_state_new.bin')
        best_accuracy = val_acc

# Testing
print("Testing:")
test_acc, test_loss = eval_model(
    model,
    test_data_loader,
    loss_fn,
    device,
    len(df_test)
)
print(f'Testing loss {test_loss} accuracy {test_acc}')

# Plotting
plt.plot(history['train_acc'], label='train accuracy')
plt.plot(history['val_acc'], label='validation accuracy')

plt.title('Training history')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.ylim([0, 1])
plt.show()
