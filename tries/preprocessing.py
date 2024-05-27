import pandas as pd
import spacy
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nlp = spacy.load("en_core_web_sm")
stopwords_ro = set(stopwords.words('romanian'))
csv_file = "./tries/model.csv"


def preprocess_text(text):
    if text.startswith("Exclusiv"):
        text = text[len("Exclusiv"):].strip()
    if text.startswith("Surse:"):
        text = text[len("Surse:"):].strip()

    text = re.sub(r'^[\[„,]+\s*', '', text)
    # Separate joined words like "preşedinteluiKlaus" to "preşedintelui Klaus"
    text = re.sub(r'([a-zăâîșțȘȚÂÎ]*)([A-ZĂÂÎȘȚ])', r'\1 \2', text)

    words = text.split()
    processed_words = [words[0]]  # Keep the first word

    for i in range(1, len(words)):
        if words[i][0].isupper() and (i == 1 or not re.match(r'[.!?]', words[i - 1][-1])):
            continue
        processed_words.append(words[i])

    text = ' '.join(processed_words)

    text = re.sub(r'[^\w\săâîșțĂÂÎȘȚ]', '', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = text.lower()

    text_tokens = text.split()
    filtered_text = [word for word in text_tokens if word not in stopwords_ro]
    text = ' '.join(filtered_text)

    return text


def tokenization(text):
    tokens = word_tokenize(text)
    return tokens


def preprocessing():
    df = pd.read_csv(csv_file)
    df['Content'] = df['Content'].apply(preprocess_text)
    df['Content'] = df['Content'].apply(tokenization)

    df.to_csv("./tries/preprocessed_model.csv", index=False, encoding='utf-8-sig')
    print("Preprocessed data saved to preprocessed_news_dataset.csv")

preprocessing()