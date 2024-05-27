import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

# Example dataset (replace with your dataset)
data = [
    ("Este o zi frumoasă", "positive"),
    ("Nu îmi place acest loc", "negative"),
    ("Mâncarea este groaznică", "negative"),
    ("Am avut o experiență plăcută", "positive"),
    ("Este destul de ok", "neutral")
]

def preprocess(text):
    # Tokenize text
    tokens = word_tokenize(text.lower())
    # Remove stopwords
    tokens = [word for word in tokens if word.isalnum()]
    stop_words = set(stopwords.words('romanian'))
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

# Apply preprocessing to the dataset
preprocessed_data = [(preprocess(text), label) for text, label in data]

# Split data into training and test sets
texts, labels = zip(*preprocessed_data)
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Convert text data to feature vectors
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Train a Naive Bayes classifier
classifier = MultinomialNB()
classifier.fit(X_train_vectorized, y_train)

# Predict on the test set
y_pred = classifier.predict(X_test_vectorized)

# Evaluate the classifier
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Function to predict sentiment of new text
def predict_sentiment(text):
    preprocessed_text = preprocess(text)
    vectorized_text = vectorizer.transform([preprocessed_text])
    prediction = classifier.predict(vectorized_text)
    return prediction[0]

# Test the prediction function
new_text = "A fost scandal la primaria capitalei."
print("Sentiment:", predict_sentiment(new_text))
