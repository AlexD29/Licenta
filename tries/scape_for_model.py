import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


def feature_extraction_and_sentiment_classification():
    # Read the preprocessed data
    df = pd.read_csv("preprocessed_model_data.csv")

    # Combine 'Title' and 'Article Content' into one text column
    df['Combined_Text'] = df['Title'] + ' ' + df['Article Content']

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(max_features=5000)  # Use top 5000 features
    X = vectorizer.fit_transform(df['Combined_Text'])

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, df['Sentiment'], test_size=0.2, random_state=42)

    # Initialize Logistic Regression model
    model = LogisticRegression(max_iter=1000)

    # Train the model
    model.fit(X_train, y_train)

    # Predict on test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy * 100:.2f}%')

    print(classification_report(y_test, y_pred))

    # Save the trained model and vectorizer
    joblib.dump(model, 'sentiment_classifier.pkl')
    joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')

    print("Model and Vectorizer saved to sentiment_classifier.pkl and tfidf_vectorizer.pkl")


feature_extraction_and_sentiment_classification()