import psycopg2

conn = psycopg2.connect(
    dbname="Licenta",
    user="postgres",
    password="password",
    host="localhost"
)

def delete_rows(conn):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tag_politician")
        cur.execute("DELETE FROM tag_city")
        cur.execute("DELETE FROM tag_political_parties")
        cur.execute("DELETE FROM article_paragraphs")
        cur.execute("DELETE FROM comments")
        cur.execute("DELETE FROM tags")
        cur.execute("DELETE FROM articles")
        conn.commit()
        print("Rows deleted successfully.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error deleting rows:", error)
        conn.rollback()

delete_rows(conn)
