import psycopg2
import pandas as pd

conn = psycopg2.connect(
    dbname="Licenta",
    user="postgres",
    password="password",
    host="localhost"
)

def insert_politicians_from_excel_to_db():
    excel_file = "politicians.xlsx"
    politicians_df = pd.read_excel(excel_file, sheet_name='Politicians')

    # Convertim coloana 'Date Of Birth' în formatul necesar
    politicians_df['Date Of Birth'] = pd.to_datetime(politicians_df['Date Of Birth'], format='%d.%m.%Y', dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

    # Eliminăm rândurile cu date invalide (NaT)
    politicians_df = politicians_df.dropna(subset=['Date Of Birth'])

    cursor = conn.cursor()

    for index, row in politicians_df.iterrows():
        values = (row['First Name'], row['Last Name'], row['City'], row['Position'], row['Description'], row['Image URL'], row['Date Of Birth'], row['Political Party Position'])
        cursor.execute('''INSERT INTO politicians (first_name, last_name, city, position, description, image_url, date_of_birth, political_party_position)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', values)

    conn.commit()
    conn.close()

def insert_political_parties_from_excel_to_db():
    excel_file="political_parties.xlsx"
    parties_df = pd.read_excel(excel_file, sheet_name='Sheet1')

    cursor = conn.cursor()

    for index, row in parties_df.iterrows():
        values = (row['Abbreviation'], row['Full Name'], row['Description'], row['Image URL'], row['Founded Year'], row['Position'], row['Ideology'])
        cursor.execute('''INSERT INTO political_parties (abbreviation, full_name, description, image_url, founded_year, position, ideology)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)''', values)

    conn.commit()
    print("Data inserted successfully.")
    conn.close()

def insert_cities_from_excel_to_db():
    excel_file="cities.xlsx"
    cities_df = pd.read_excel(excel_file, sheet_name='Cities')
    cursor = conn.cursor()
    for index, row in cities_df.iterrows():
        values = (row['Name'], row['Description'], row['Image URL'], row['Population'])
        cursor.execute('''INSERT INTO cities (name, description, image_url, population)
                            VALUES (%s, %s, %s, %s)''', values)
    conn.commit()
    print("Data inserted successfully.")

#insert_politicians_from_excel_to_db()

#insert_cities_from_excel_to_db()
    
#insert_political_parties_from_excel_to_db()

def update_political_party_column_from_excel():
    excel_file = "politicians.xlsx"
    politicians_df = pd.read_excel(excel_file, sheet_name='Politicians')

    # Convert 'Date Of Birth' column to the necessary format
    politicians_df['Date Of Birth'] = pd.to_datetime(politicians_df['Date Of Birth'], format='%d.%m.%Y', dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

    # Remove rows with invalid dates (NaT)
    politicians_df = politicians_df.dropna(subset=['Date Of Birth'])

    cursor = conn.cursor()

    for index, row in politicians_df.iterrows():
        first_name = row['First Name']
        last_name = row['Last Name']
        party_abbreviation = row['Political Party']
        
        if pd.isna(party_abbreviation):
            continue

        # Find the politician in the database
        cursor.execute("""
            SELECT id FROM politicians WHERE first_name = %s AND last_name = %s
        """, (first_name, last_name))
        politician_id = cursor.fetchone()

        if politician_id:
            politician_id = politician_id[0]

            # Find the party id from the political_parties table using the abbreviation
            cursor.execute("""
                SELECT id FROM political_parties WHERE abbreviation = %s
            """, (party_abbreviation,))
            party_id = cursor.fetchone()

            if party_id:
                party_id = party_id[0]
                # Update the political party column for the politician
                cursor.execute("""
                    UPDATE politicians SET political_party_id = %s WHERE id = %s
                """, (party_id, politician_id))

    conn.commit()
    conn.close()

# Run the function to update political parties
update_political_party_column_from_excel()