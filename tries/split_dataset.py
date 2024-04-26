import random
import csv
import psycopg2

conn = psycopg2.connect(
    dbname="Licenta",
    user="postgres",
    password="password",
    host="localhost"
)
cur = conn.cursor()

csv_file = "model_data.csv"


def clean_text_from_database(text):
    if isinstance(text, (tuple, list)):
        text = text[0]

    if text.startswith("['") and text.endswith("']"):
        text = text[2:-2]  # Remove the first 2 and last 2 characters
    return text


global_index = 0


def get_articles_from_db_and_append(csv_file, table_name, limit=203):
    global global_index  # Access the global counter

    try:
        with open(csv_file, 'x', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Index', 'Content', 'Emotion'])
    except FileExistsError:
        pass

    query = f"SELECT article_text FROM {table_name} ORDER BY RANDOM() LIMIT {limit};"
    cur.execute(query)
    articles = cur.fetchall()

    emotions = ["Bucurie", "Furie", "Frica", "Tristete", "Neutru"]

    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)

        for article in articles:
            article_text_value = article[0]
            if isinstance(article_text_value, tuple):  # Check if it's a tuple
                article_text = article_text_value[0]  # Extract the string from the tuple
            else:
                article_text = article_text_value

            cleaned_article_text = clean_text_from_database(article_text)

            # Randomly assign an emotion
            emotion = random.choice(emotions)

            global_index += 1  # Increment the global counter
            writer.writerow([global_index, cleaned_article_text, emotion])

    print(f"Articles from {table_name} appended to {csv_file}")

# Function to split the dataset into validation and test sets
def split_dataset(csv_file, val_file, test_file, val_size, test_size):
    with open(csv_file, 'r', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        articles = list(reader)

        # Split the dataset
        val_data = articles[:val_size]
        test_data = articles[val_size:val_size + test_size]

    # Write the split datasets to separate CSV files
    write_to_csv(val_file, val_data)
    write_to_csv(test_file, test_data)


def write_to_csv(file_name, data):
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Index', 'Content', 'Emotion']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for idx, row in enumerate(data, start=1):
            writer.writerow({'Index': idx, 'Content': row['Content'], 'Emotion': row['Emotion']})

# Define the filenames for validation and test sets
val_file = "../data/val_with_titles.csv"
test_file = "../data/test_with_titles.csv"

get_articles_from_db_and_append(csv_file, "scraped_articles")
get_articles_from_db_and_append(csv_file, "digi24_articles")
get_articles_from_db_and_append(csv_file, "mediafax_articles")
get_articles_from_db_and_append(csv_file, "protv_articles")

# Split the dataset
split_dataset(csv_file, val_file, test_file, 406, 406)
