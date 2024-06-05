import psycopg2
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask import request
import os
import bcrypt
import secrets
from flask import g
from datetime import datetime
from flask import jsonify
from .models import db
from .queries import query_politicians, query_political_parties, query_cities, query_tags


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/Licenta'
db.init_app(app)

@app.before_request
def before_request():
    g.db_conn = get_db_connection()
    g.db_cursor = g.db_conn.cursor()

@app.after_request
def after_request(response):
    g.db_cursor.close()
    g.db_conn.close()
    return response

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
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        offset = (page - 1) * limit

        cur = g.db_cursor

        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion
            FROM articles AS a
            ORDER BY a.published_date DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

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
                'emotion': article[8],
                'source': article[7]
            }
            articles_list.append(article_dict)

        cur.execute("SELECT COUNT(*) FROM articles")
        total_articles = cur.fetchone()[0]

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
        cur = g.db_cursor

        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion
            FROM articles AS a
            WHERE a.id = %s
        """, (article_id,))
        article_data = cur.fetchone()

        if article_data is None:
            return jsonify({"error": "Article not found"}), 404

        cur.execute("""
            SELECT tag_text
            FROM tags
            WHERE article_id = %s
        """, (article_id,))
        tags = [tag[0] for tag in cur.fetchall()]

        cur.execute("""
            SELECT paragraph_text
            FROM article_paragraphs
            WHERE article_id = %s
        """, (article_id,))
        article_text = [paragraph[0] for paragraph in cur.fetchall()]

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
            'emotion': article_data[8],
            'source': article_data[7]
        }

        return jsonify({"article": article_dict})

    except Exception as e:
        print("Error fetching article:", e)
        return jsonify({"error": "Failed to fetch article"}), 500

@app.route('/api/articles/today', methods=['GET'])
def get_today_articles():
    try:
        today_date = datetime.now().date()

        cur = g.db_cursor

        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion
            FROM articles AS a
            WHERE DATE(a.published_date) = %s
            ORDER BY a.published_date DESC
        """, (today_date,))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

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
                'emotion': article[8],
                'source': article[7]
            }
            articles_list.append(article_dict)

        return jsonify({
            'articles': articles_list,
        })

    except Exception as e:
        print("Error fetching today's articles:", e)
        return jsonify({"error": "Failed to fetch today's articles"}), 500

@app.route('/api/politician_articles', methods=['GET'])
def politician_articles():
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT id, first_name, last_name, image_url
            FROM politicians
        """)
        politicians = cur.fetchall()

        politician_articles_data = []

        for politician in politicians:
            cur.execute("""
                SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
                FROM articles AS a
                JOIN tags AS t ON a.id = t.article_id
                WHERE t.tag_text IN (
                    SELECT tag_text
                    FROM tag_politician
                    JOIN tags ON tag_politician.tag_id = tags.id
                    WHERE politician_id = %s
                )
                ORDER BY a.published_date DESC
            """, (politician[0],))
            articles = cur.fetchall()

            articles_list = []
            for article in articles:
                cur.execute("""
                    SELECT tag_text
                    FROM tags
                    WHERE article_id = %s
                """, (article[0],))
                tags = [tag[0] for tag in cur.fetchall()]

                cur.execute("""
                    SELECT paragraph_text
                    FROM article_paragraphs
                    WHERE article_id = %s
                """, (article[0],))
                article_text = [paragraph[0] for paragraph in cur.fetchall()]

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

            politician_dict = {
                'politician_id': politician[0],
                'first_name': politician[1],
                'last_name': politician[2],
                'image_url': politician[3],
                'articles': articles_list
            }

            politician_articles_data.append(politician_dict)

        return jsonify(politician_articles_data)

    except Exception as e:
        print("Error fetching politician articles:", e)
        return jsonify({"error": "Failed to fetch politician articles"}), 500

@app.route('/api/politician_articles/<int:politician_id>', methods=['GET'])
def politician_articles_by_id(politician_id):
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT id, first_name, last_name, image_url
            FROM politicians
            WHERE id = %s
        """, (politician_id,))
        politician = cur.fetchone()

        if not politician:
            return jsonify({"error": "Politician not found"}), 404

        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
            FROM articles AS a
            JOIN tags AS t ON a.id = t.article_id
            WHERE t.tag_text IN (
                SELECT tag_text
                FROM tag_politician
                JOIN tags ON tag_politician.tag_id = tags.id
                WHERE politician_id = %s
            )
            ORDER BY a.published_date DESC
        """, (politician[0],))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

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

        politician_dict = {
            'politician_id': politician[0],
            'first_name': politician[1],
            'last_name': politician[2],
            'image_url': politician[3],
            'articles': articles_list
        }

        return jsonify(politician_dict)

    except Exception as e:
        print("Error fetching politician articles:", e)
        return jsonify({"error": "Failed to fetch politician articles"}), 500

@app.route('/api/explore', methods=['GET'])
def explore_data():
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
            FROM articles AS a
            ORDER BY a.published_date DESC
        """)
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

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

        cur.execute("""
            SELECT id, first_name, last_name, city, position, image_url, age
            FROM politicians
        """)
        politicians = cur.fetchall()

        politician_data = []
        for politician in politicians:
            cur.execute("""
                SELECT tag_text
                FROM tag_politician
                JOIN tags ON tag_politician.tag_id = tags.id
                WHERE politician_id = %s
            """, (politician[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            politician_dict = {
                'id': politician[0],
                'first_name': politician[1],
                'last_name': politician[2],
                'city': politician[3],
                'position': politician[4],
                'image_url': politician[5],
                'age': politician[6],
                'tags': tags
            }
            politician_data.append(politician_dict)

        cur.execute("""
            SELECT id, name, description, image_url, candidates_for_mayor, mayor
            FROM cities
        """)
        cities = cur.fetchall()

        city_data = []
        for city in cities:
            cur.execute("""
                SELECT tag_text
                FROM tag_city
                JOIN tags ON tag_city.tag_id = tags.id
                WHERE city_id = %s
            """, (city[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            city_dict = {
                'id': city[0],
                'name': city[1],
                'description': city[2],
                'image_url': city[3],
                'candidates_for_mayor': city[4],
                'mayor': city[5],
                'tags': tags
            }
            city_data.append(city_dict)

        cur.execute("""
            SELECT id, abbreviation, full_name, description, image_url
            FROM political_parties
        """)
        political_parties = cur.fetchall()

        party_data = []
        for party in political_parties:
            cur.execute("""
                SELECT tag_text
                FROM tag_political_parties
                JOIN tags ON tag_political_parties.tag_id = tags.id
                WHERE political_party_id = %s
            """, (party[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            party_dict = {
                'id': party[0],
                'abbreviation': party[1],
                'full_name': party[2],
                'description': party[3],
                'image_url': party[4],
                'tags': tags
            }
            party_data.append(party_dict)

        return jsonify({
            'articles': articles_list,
            'politicians': politician_data,
            'cities': city_data,
            'political_parties': party_data
        })

    except Exception as e:
        print("Error fetching explore data:", e)
        return jsonify({"error": "Failed to fetch explore data"}), 500

@app.route('/api/politicians', methods=['GET'])
def politicians_data():
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT id, first_name, last_name, city, position, image_url, age
            FROM politicians
        """)
        politicians = cur.fetchall()

        politician_data = []
        for politician in politicians:
            cur.execute("""
                SELECT tag_text
                FROM tag_politician
                JOIN tags ON tag_politician.tag_id = tags.id
                WHERE politician_id = %s
            """, (politician[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            politician_dict = {
                'id': politician[0],
                'first_name': politician[1],
                'last_name': politician[2],
                'city': politician[3],
                'position': politician[4],
                'image_url': politician[5],
                'age': politician[6],
                'tags': tags
            }
            politician_data.append(politician_dict)

        return jsonify({
            'politicians': politician_data
        })

    except Exception as e:
        print("Error fetching explore data:", e)
        return jsonify({"error": "Failed to fetch explore data"}), 500

@app.route('/api/political-parties', methods=['GET'])
def political_parties_data():
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT id, abbreviation, full_name, description, image_url
            FROM political_parties
        """)
        political_parties = cur.fetchall()

        party_data = []
        for party in political_parties:
            cur.execute("""
                SELECT tag_text
                FROM tag_political_parties
                JOIN tags ON tag_political_parties.tag_id = tags.id
                WHERE political_party_id = %s
            """, (party[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            party_dict = {
                'id': party[0],
                'abbreviation': party[1],
                'full_name': party[2],
                'description': party[3],
                'image_url': party[4],
                'tags': tags
            }
            party_data.append(party_dict)

        return jsonify({
            'political_parties': party_data
        })

    except Exception as e:
        print("Error fetching explore data:", e)
        return jsonify({"error": "Failed to fetch explore data"}), 500

@app.route('/api/cities', methods=['GET'])
def cities_data():
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT id, name, description, image_url, candidates_for_mayor, mayor
            FROM cities
        """)
        cities = cur.fetchall()

        city_data = []
        for city in cities:
            cur.execute("""
                SELECT tag_text
                FROM tag_city
                JOIN tags ON tag_city.tag_id = tags.id
                WHERE city_id = %s
            """, (city[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            city_dict = {
                'id': city[0],
                'name': city[1],
                'description': city[2],
                'image_url': city[3],
                'candidates_for_mayor': city[4],
                'mayor': city[5],
                'tags': tags
            }
            city_data.append(city_dict)

        return jsonify({
            'cities': city_data
        })

    except Exception as e:
        print("Error fetching explore data:", e)
        return jsonify({"error": "Failed to fetch explore data"}), 500

def get_articles_by_politician_id(politician_id):
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
            FROM articles AS a
            JOIN tags AS t ON a.id = t.article_id
            WHERE t.tag_text IN (
                SELECT tag_text
                FROM tag_politician
                JOIN tags ON tag_politician.tag_id = tags.id
                WHERE politician_id = %s
            )
            ORDER BY a.published_date ASC
        """, (politician_id,))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

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

        return articles_list

    except Exception as e:
        print("Error fetching articles for politician:", e)
        return []

def get_articles_by_political_party_id(political_party_id):
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
            FROM articles AS a
            JOIN tags AS t ON a.id = t.article_id
            WHERE t.tag_text IN (
                SELECT tag_text
                FROM tag_political_parties
                JOIN tags ON tag_political_parties.tag_id = tags.id
                WHERE political_party_id = %s
            )
            ORDER BY a.published_date ASC
        """, (political_party_id,))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

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

        return articles_list

    except Exception as e:
        print("Error fetching articles for political party:", e)
        return []

def get_articles_by_city_id(city_id):
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source
            FROM articles AS a
            JOIN tags AS t ON a.id = t.article_id
            WHERE t.tag_text IN (
                SELECT tag_text
                FROM tag_city
                JOIN tags ON tag_city.tag_id = tags.id
                WHERE city_id = %s
            )
            ORDER BY a.published_date ASC
        """, (city_id,))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("""
                SELECT paragraph_text
                FROM article_paragraphs
                WHERE article_id = %s
            """, (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

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

        return articles_list

    except Exception as e:
        print("Error fetching articles for city:", e)
        return []

@app.route('/api/suggestions')
def get_suggestions():
    query = request.args.get('query')
    politician_suggestions = query_politicians(query)
    political_parties_suggestions = query_political_parties(query)
    cities_suggestions = query_cities(query)
    
    suggestions_from_entities = politician_suggestions + political_parties_suggestions + cities_suggestions
    if suggestions_from_entities:
        if len(suggestions_from_entities) == 1:
            single_suggestion = suggestions_from_entities[0]
            articles = []
            if single_suggestion['category'] == 'Politician':
                politician_id = single_suggestion['id']
                articles = get_articles_by_politician_id(politician_id)
            elif single_suggestion['category'] == 'Partid politic':
                political_party_id = single_suggestion['id']
                articles = get_articles_by_political_party_id(political_party_id)
            elif single_suggestion['category'] == 'Oraș':
                city_id = single_suggestion['id']
                articles = get_articles_by_city_id(city_id)

            article_suggestions = [{
                'title': article['title'],
                'url': article['url'],
                'author': article['author'],
                'published_date': article['published_date'],
                'number_of_views': article['number_of_views'],
                'image_url': article['image_url'],
                'source': article['source'],
                'category': 'Article'
            } for article in articles[:4]]

            suggestions = suggestions_from_entities[:5] + article_suggestions
            return jsonify(suggestions[:5])

        suggestions = suggestions_from_entities[:5]
        return jsonify(suggestions)

    tags_suggestions = query_tags(query)
    suggestions = tags_suggestions[:5]
    return jsonify(suggestions)

def generate_session_token():
    return secrets.token_hex(16)

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = g.db_cursor

        cur.execute("SELECT get_next_user_id()")
        next_user_id = cur.fetchone()[0] + 1

        cur.execute("INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s) RETURNING email", (next_user_id, email, hashed_password.decode('utf-8')))
        new_user_email = cur.fetchone()[0]

        g.db_conn.commit()

        session_token = generate_session_token()
        cur.execute("UPDATE users SET session_token = %s WHERE email = %s", (session_token, email))
        g.db_conn.commit()

        return jsonify({
            'id': next_user_id,
            'email': new_user_email,
            'session_token': session_token
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

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        cur = g.db_cursor

        cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return jsonify({"error": "Invalid email or password"}), 401
        
        session_token = generate_session_token()
        cur.execute("UPDATE users SET session_token = %s WHERE id = %s", (session_token, user[0]))
        g.db_conn.commit()

        return jsonify({
            'id': user[0],
            'email': user[1],
            'session_token': session_token
        }), 200

    except Exception as e:
        print("Error logging in:", e)
        return jsonify({"error": "Failed to login"}), 500
    
@app.route('/api/protected', methods=['GET'])
def protected_route():
    try:
        session_token = request.cookies.get('session_token')

        if not session_token:
            return jsonify({"error": "Session token is required"}), 401

        cur = g.db_cursor

        cur.execute("SELECT * FROM users WHERE session_token = %s", (session_token,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Invalid session token"}), 401

        return jsonify({"message": "You are authorized to access this resource"}), 200

    except Exception as e:
        print("Error accessing protected route:", e)
        return jsonify({"error": "Failed to access protected route"}), 500

