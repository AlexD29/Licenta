import psycopg2
import pandas as pd

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="Licenta",
    user="postgres",
    password="password",
    host="localhost"
)

# Create a cursor object
cur = conn.cursor()

# SQL query to fetch titles from the articles table
cur.execute("SELECT id, title FROM articles")
articles = cur.fetchall()

# Create a list to hold the rows for the CSV
csv_data = []

for article_id, title in articles:
    # SQL query to fetch the first two paragraphs from the article_paragraphs table
    cur.execute("""
        SELECT paragraph_text 
        FROM article_paragraphs 
        WHERE article_id = %s 
        ORDER BY id
        LIMIT 2
    """, (article_id,))
    paragraphs = cur.fetchall()
    
    # Concatenate the title and the first two paragraphs
    content = title + "\n" + "\n".join([paragraph[0] for paragraph in paragraphs])
    
    # Append the data to the list
    csv_data.append([len(csv_data) + 1, content, ''])

# Close the cursor and the connection
cur.close()
conn.close()

# Create a DataFrame from the data
df = pd.DataFrame(csv_data, columns=['Index', 'Content', 'Label'])

# Write the DataFrame to a CSV file
df.to_csv('./tries/model.csv', index=False)
