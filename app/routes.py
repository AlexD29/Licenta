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
        cur.execute("SELECT * FROM articles ORDER BY published_date DESC LIMIT %s OFFSET %s", (limit, offset))
        articles = cur.fetchall()

        # Fetch total number of articles for pagination
        cur.execute("SELECT COUNT(*) FROM articles")
        total_articles = cur.fetchone()[0]

        cur.close()
        conn.close()

        articles_list = []
        for article in articles:
            article_dict = {
                'id': article[0],
                'title': article[1],
                'url': article[2],
                'author': article[3],
                'published_date': article[4],
                'number_of_views': article[5],
                'tags': article[6],
                'image_url': article[7],
                'article_text': article[8],
                'comments': article[9],
                'source': article[10]
            }
            articles_list.append(article_dict)

        # Calculate total pages
        total_pages = (total_articles + limit - 1) // limit

        return jsonify({
            'articles': articles_list,
            'totalPages': total_pages
        })

    except Exception as e:
        print("Error fetching articles:", e)
        return jsonify({"error": "Failed to fetch articles"}), 500
    

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
