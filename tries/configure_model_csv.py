import csv
import random
import psycopg2
import pandas as pd
import spacy
import re
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import word_tokenize

conn = psycopg2.connect(
    dbname="Licenta",
    user="postgres",
    password="password",
    host="localhost"
)
cur = conn.cursor()

nlp = spacy.load("en_core_web_sm")
stopwords_ro = set(stopwords.words('romanian'))
csv_file = "model_data.csv"


def clean_text_from_database(text):
    if text.startswith("['") and text.endswith("']"):
        text = text[2:-2]  # Remove the first 2 and last 2 characters
    return text

def get_articles_from_db_and_append(csv_file, table_name, limit=200):
    try:
        with open(csv_file, 'x', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Article Content', 'Sentiment'])
    except FileExistsError:
        pass

    query = f"SELECT title, article_text FROM {table_name} ORDER BY RANDOM() LIMIT {limit};"
    cur.execute(query)
    articles = cur.fetchall()

    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)

        for article in articles:
            title, article_text_value = article
            if isinstance(article_text_value, (tuple, list)):
                article_text = article_text_value[0]
            else:
                article_text = article_text_value

            cleaned_article_text = clean_text_from_database(article_text)
            writer.writerow([title, cleaned_article_text, ''])

    print(f"Articles from {table_name} appended to {csv_file}")


get_articles_from_db_and_append(csv_file, "scraped_articles")
get_articles_from_db_and_append(csv_file, "digi24_articles")
get_articles_from_db_and_append(csv_file, "mediafax_articles")
get_articles_from_db_and_append(csv_file, "protv_articles")


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


def assign_random_sentiment():
    sentiments = ["Positive", "Negative", "Neutral"]
    return random.choice(sentiments)

def preprocessing():
    df = pd.read_csv(csv_file)
    df['Title'] = df['Title'].apply(preprocess_text)
    df['Title'] = df['Title'].apply(tokenization)
    df['Article Content'] = df['Article Content'].apply(preprocess_text)
    df['Article Content'] = df['Article Content'].apply(tokenization)

    df['Sentiment'] = df.apply(lambda x: assign_random_sentiment(), axis=1)

    df.to_csv("preprocessed_model_data.csv", index=False, encoding='utf-8-sig')
    print("Preprocessed data saved to preprocessed_news_dataset.csv")


# preprocessing()


# import joblib
# import re
# from nltk.tokenize import word_tokenize
#
# # Load the trained model and vectorizer
# clf = joblib.load('sentiment_classifier.pkl')
# tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')
#
# # New text to test
# new_text = "A fost scandal in Barcelona."
#
# # Preprocess the new text
# new_text_processed = preprocess_text(new_text)
#
# # Transform the new text into TF-IDF features
# new_text_tfidf = tfidf_vectorizer.transform([new_text_processed])
#
# # Predict the sentiment of the new text
# predicted_sentiment = clf.predict(new_text_tfidf)[0]
#
# print(f"Predicted Sentiment: {predicted_sentiment}")