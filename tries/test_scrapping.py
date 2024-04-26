import joblib
import re
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the trained model and vectorizer
clf = joblib.load('sentiment_classifier.pkl')
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')

# New text to test
new_text = "This is a great movie!"

# Preprocess the new text
new_text_processed = preprocess_text(new_text)

# Transform the new text into TF-IDF features
new_text_tfidf = tfidf_vectorizer.transform([new_text_processed])

# Predict the sentiment of the new text
predicted_sentiment = clf.predict(new_text_tfidf)[0]

print(f"Predicted Sentiment: {predicted_sentiment}")