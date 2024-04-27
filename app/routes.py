import psycopg2
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask import request
import os
import bcrypt

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(
        dbname="Licenta",
        user="postgres",
        password="password",
        host="localhost"
    )
    return conn

@app.route('/')
def index():
    return send_from_directory(os.path.join('my-react-app', 'build'), 'index.html')

@app.route('/static/js/<path:path>')
def serve_js(path):
    return send_from_directory(os.path.join('my-react-app', 'build', 'static', 'js'), path)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory(os.path.join('my-react-app', 'build', 'static', 'css'), path)

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(os.path.join('my-react-app', 'build'), path)


@app.route('/api/articles', methods=['GET'])
def get_articles():
    try:
        # Get query parameters for pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))  # Default limit to 10 articles per page

        # Calculate offset based on page and limit
        offset = (page - 1) * limit

        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch articles with pagination
        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
            FROM articles AS a
            ORDER BY a.published_date DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            # Fetch tags for the article
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            # Fetch article paragraphs
            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

            # Fetch comments for the article
            cur.execute("""
                SELECT comment_text
                FROM comments
                WHERE article_id = %s
            """, (article[0],))
            comments = [comment[0] for comment in cur.fetchall()]

            article_dict = {
                'id': article[0],
                'title': article[1],
                'url': article[2],
                'author': article[3],
                'published_date': article[4],
                'number_of_views': article[5],
                'tags': tags,
                'image_url': article[6],
                'article_text': article_text,
                'comments': comments,
                'source': article[7]
            }
            articles_list.append(article_dict)

        # Calculate total number of articles for pagination
        cur.execute("SELECT COUNT(*) FROM articles")
        total_articles = cur.fetchone()[0]

        cur.close()
        conn.close()

        # Calculate total pages
        total_pages = (total_articles + limit - 1) // limit

        return jsonify({
            'articles': articles_list,
            'totalPages': total_pages
        })

    except Exception as e:
        print("Error fetching articles:", e)
        return jsonify({"error": "Failed to fetch articles"}), 500

@app.route('/api/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch article by ID
        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
            FROM articles AS a
            WHERE a.id = %s
        """, (article_id,))
        article_data = cur.fetchone()

        if article_data is None:
            return jsonify({"error": "Article not found"}), 404

        # Fetch tags for the article
        cur.execute("""
            SELECT tag_text
            FROM tags
            WHERE article_id = %s
        """, (article_id,))
        tags = [tag[0] for tag in cur.fetchall()]

        # Fetch article paragraphs
        cur.execute("""
            SELECT paragraph_text
            FROM article_paragraphs
            WHERE article_id = %s
        """, (article_id,))
        article_text = [paragraph[0] for paragraph in cur.fetchall()]

        # Fetch comments for the article
        cur.execute("""
            SELECT comment_text
            FROM comments
            WHERE article_id = %s
        """, (article_id,))
        comments = [comment[0] for comment in cur.fetchall()]

        article_dict = {
            'id': article_data[0],
            'title': article_data[1],
            'url': article_data[2],
            'author': article_data[3],
            'published_date': article_data[4],
            'number_of_views': article_data[5],
            'tags': tags,
            'image_url': article_data[6],
            'article_text': article_text,
            'comments': comments,
            'source': article_data[7]
        }

        cur.close()
        conn.close()

        return jsonify({"article": article_dict})

    except Exception as e:
        print("Error fetching article:", e)
        return jsonify({"error": "Failed to fetch article"}), 500





@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if email or password is missing
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor()

        # Get the next user ID using the get_next_user_id() function
        cur.execute("SELECT get_next_user_id()")
        next_user_id = cur.fetchone()[0] + 1

        # Insert user into the database
        cur.execute("INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s) RETURNING email", (next_user_id, email, hashed_password.decode('utf-8')))
        new_user_email = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'id': next_user_id,
            'email': new_user_email
        }), 201

    except Exception as e:
        print("Error signing up:", e)
        return jsonify({"error": "Failed to signup"}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if email or password is missing
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch user by email
        cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401

        # TODO: Generate and save token for user session
        # For now, return user info
        return jsonify({
            'id': user[0],
            'email': user[1]
        }), 200

    except Exception as e:
        print("Error logging in:", e)
        return jsonify({"error": "Failed to login"}), 500
