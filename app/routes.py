import psycopg2
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask import request
import os
import bcrypt
import secrets
import random
from flask import g
from datetime import datetime, timedelta, date
from .models import db
from .queries import *
from .db import before_request, after_request
from .stats_routes import statistics_bp

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re

stop_words_ro = set(stopwords.words('romanian'))

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/Licenta'
db.init_app(app)

app.before_request(before_request)
app.after_request(after_request)

app.register_blueprint(statistics_bp)

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

        # Step 1: Fetch the articles
        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion,
                   s.name AS source_name, s.image_url AS source_image_url
            FROM articles AS a
            JOIN sources AS s ON a.source = s.id
            ORDER BY a.published_date DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        articles = cur.fetchall()

        articles_list = []
        article_ids = [article[0] for article in articles]

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
                'source_name': article[9],
                'source_image_url': article[10]
            }
            articles_list.append(article_dict)

        # Step 2: Retrieve related entities for the articles
        if article_ids:
            cur.execute("""
                WITH article_tags AS (
                    SELECT t.article_id, t.id, t.tag_text
                    FROM tags t
                    WHERE t.article_id = ANY(%s)
                ),
                all_entities AS (
                    SELECT
                        at.article_id,
                        'politician' AS entity_type,
                        tp.politician_id AS entity_id,
                        CONCAT(p.first_name, ' ', p.last_name) AS entity_name,
                        p.image_url
                    FROM article_tags at
                    JOIN tag_politician tp ON at.tag_text = (
                        SELECT t2.tag_text
                        FROM tags t2
                        WHERE t2.id = tp.tag_id
                    )
                    JOIN politicians p ON tp.politician_id = p.id
                    UNION ALL
                    SELECT
                        at.article_id,
                        'political-party' AS entity_type,
                        tp.political_party_id AS entity_id,
                        pp.abbreviation AS entity_name,
                        pp.image_url
                    FROM article_tags at
                    JOIN tag_political_parties tp ON at.tag_text = (
                        SELECT t2.tag_text
                        FROM tags t2
                        WHERE t2.id = tp.tag_id
                    )
                    JOIN political_parties pp ON tp.political_party_id = pp.id
                    UNION ALL
                    SELECT
                        at.article_id,
                        'city' AS entity_type,
                        tc.city_id AS entity_id,
                        c.name AS entity_name,
                        c.image_url
                    FROM article_tags at
                    JOIN tag_city tc ON at.tag_text = (
                        SELECT t2.tag_text
                        FROM tags t2
                        WHERE t2.id = tc.tag_id
                    )
                    JOIN cities c ON tc.city_id = c.id
                ),
                entity_counts AS (
                    SELECT
                        entity_type,
                        entity_id,
                        entity_name,
                        image_url,
                        COUNT(*) as entity_count
                    FROM all_entities
                    GROUP BY entity_type, entity_id, entity_name, image_url
                )
                SELECT
                    entity_type,
                    entity_id,
                    entity_name,
                    image_url,
                    entity_count
                FROM entity_counts
                ORDER BY entity_type, entity_count DESC
            """, (article_ids,))
            related_entities = cur.fetchall()

            # Step 3: Organize and count the entities
            top_entities = {'politician': [], 'political-party': [], 'city': []}

            for entity in related_entities:
                entity_type, entity_id, entity_name, image_url, entity_count = entity
                top_entities[entity_type].append({
                    'entity_id': entity_id,
                    'entity_name': entity_name,
                    'image_url': image_url,
                    'entity_count': entity_count
                })

        cur.execute("SELECT COUNT(*) FROM articles")
        total_articles = cur.fetchone()[0]

        total_pages = (total_articles + limit - 1) // limit

        return jsonify({
            'articles': articles_list,
            'totalPages': total_pages,
            'top_entities': top_entities
        })

    except Exception as e:
        print("Error fetching articles:", e)
        return jsonify({"error": "Failed to fetch articles"}), 500

@app.route('/api/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion,
                   s.name AS source_name, s.image_url AS source_image_url
            FROM articles AS a
            JOIN sources AS s ON a.source = s.id
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
            'source_id': article_data[7],
            'source_name': article_data[9],
            'source_image_url': article_data[10]
        }

        return jsonify({"article": article_dict})

    except Exception as e:
        print("Error fetching article:", e)
        return jsonify({"error": "Failed to fetch article"}), 500

@app.route('/api/article-suggestions/<int:article_id>', methods=['GET'])
def get_article_suggestions(article_id):
    try:
        # Fetch the current article details
        cur = g.db_cursor

        cur.execute("""
            SELECT a.title, a.image_url, a.emotion, a.source, s.name, s.image_url
            FROM articles a
            JOIN sources s ON a.source = s.id
            WHERE a.id = %s
        """, (article_id,))
        current_article = cur.fetchone()
        if not current_article:
            return jsonify({"error": "Article not found"}), 404
        
        current_article_title = current_article[0]
        current_article_image = current_article[1]
        current_article_emotion = current_article[2]
        current_article_source_id = current_article[3]
        current_article_source_name = current_article[4]
        current_article_source_image = current_article[5]

        # Fetch all other articles' details
        cur.execute("""
            SELECT a.id, a.title, a.image_url, a.emotion, a.url, s.id, s.name, s.image_url
            FROM articles a
            JOIN sources s ON a.source = s.id
            WHERE a.id != %s
        """, (article_id,))
        articles = cur.fetchall()

        # Preprocess article titles for Romanian
        def preprocess_text_ro(text):
            # Remove non-alphanumeric characters
            text = re.sub(r'\W', ' ', text)
            # Convert to lowercase
            text = text.lower()
            # Tokenize words
            words = word_tokenize(text)
            # Remove stopwords
            words = [word for word in words if word not in stop_words_ro]
            # Join words back into a single string
            return ' '.join(words)

        # Preprocess current article title
        current_article_title = preprocess_text_ro(current_article_title)

        # Preprocess all other article titles
        article_titles = [preprocess_text_ro(article[1]) for article in articles]

        # Vectorize article titles
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform([current_article_title] + article_titles)

        # Calculate cosine similarity
        similarities = cosine_similarity(X[0], X[1:]).flatten()

        # Get indices of top 5 similar articles
        top_indices = similarities.argsort()[-5:][::-1]

        # Retrieve details of top 5 similar articles with additional info
        suggested_articles = []
        for idx in top_indices:
            article = articles[idx]
            suggested_articles.append({
                'id': article[0],
                'title': article[1],
                'url': article[4],  # Directly using the url column from the articles table
                'image_url': article[2],
                'emotion': article[3],
                'source': {
                    'id': article[5],
                    'name': article[6],
                    'image_url': article[7]
                }
            })

        return jsonify({"suggested_articles": suggested_articles})

    except Exception as e:
        print("Error fetching article suggestions:", e)
        return jsonify({"error": "Failed to fetch article suggestions"}), 500

@app.route('/api/politician_articles', methods=['GET'])
def politician_articles():
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT id, first_name, last_name, image_url
            FROM politicians
        """)
        politicians = cur.fetchall()

        random.shuffle(politicians)

        politician_articles_data = []

        for politician in politicians:
            cur.execute("""
                SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion
                FROM articles AS a
                JOIN tags AS t ON a.id = t.article_id
                WHERE t.tag_text IN (
                    SELECT tag_text
                    FROM tag_politician
                    JOIN tags ON tag_politician.tag_id = tags.id
                    WHERE politician_id = %s
                )
                ORDER BY a.published_date DESC
                LIMIT 5
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
                    'source': article[7],
                    'emotion': article[8]
                }
                articles_list.append(article_dict)

            politician_dict = {
                'id': politician[0],
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

@app.route('/api/political_parties_articles', methods=['GET'])
def political_parties_articles():
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT id, abbreviation, image_url
            FROM political_parties
        """)
        political_parties = cur.fetchall()

        random.shuffle(political_parties)

        political_parties_articles_data = []

        for party in political_parties:
            cur.execute("""
                SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion
                FROM articles AS a
                JOIN tags AS t ON a.id = t.article_id
                WHERE t.tag_text IN (
                    SELECT tag_text
                    FROM tag_political_parties
                    JOIN tags ON tag_political_parties.tag_id = tags.id
                    WHERE political_party_id = %s
                )
                ORDER BY a.published_date DESC
                LIMIT 5
            """, (party[0],))
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
                    'source': article[7],
                    'emotion': article[8]
                }
                articles_list.append(article_dict)

            party_dict = {
                'id': party[0],
                'abbreviation': party[1],
                'image_url': party[2],
                'articles': articles_list
            }

            political_parties_articles_data.append(party_dict)

        return jsonify(political_parties_articles_data)

    except Exception as e:
        print("Error fetching political parties articles:", e)
        return jsonify({"error": "Failed to fetch political parties articles"}), 500

@app.route('/api/cities_articles', methods=['GET'])
def cities_articles():
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT id, name, image_url
            FROM cities
        """)
        cities = cur.fetchall()

        random.shuffle(cities)

        cities_articles_data = []

        for city in cities:
            cur.execute("""
                SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion
                FROM articles AS a
                JOIN tags AS t ON a.id = t.article_id
                WHERE t.tag_text IN (
                    SELECT tag_text
                    FROM tag_city
                    JOIN tags ON tag_city.tag_id = tags.id
                    WHERE city_id = %s
                )
                ORDER BY a.published_date DESC
                LIMIT 5
            """, (city[0],))
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
                    'source': article[7],
                    'emotion': article[8]
                }
                articles_list.append(article_dict)

            city_dict = {
                'id': city[0],
                'name': city[1],
                'image_url': city[2],
                'articles': articles_list
            }

            cities_articles_data.append(city_dict)

        return jsonify(cities_articles_data)

    except Exception as e:
        print("Error fetching political parties articles:", e)
        return jsonify({"error": "Failed to fetch political parties articles"}), 500

@app.route('/api/sources_articles', methods=['GET'])
def sources_articles():
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT id, name, image_url
            FROM sources
        """)
        sources = cur.fetchall()

        random.shuffle(sources)

        sources_articles_data = []

        for source in sources:
            cur.execute("""
                SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion
                FROM articles AS a
                WHERE a.source = %s
                ORDER BY a.published_date DESC
                LIMIT 5
            """, (source[0],))
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
                    'source': article[7],
                    'emotion': article[8]
                }
                articles_list.append(article_dict)

            source_dict = {
                'id': source[0],
                'name': source[1],
                'image_url': source[2],
                'articles': articles_list
            }

            sources_articles_data.append(source_dict)

        return jsonify(sources_articles_data)

    except Exception as e:
        print("Error fetching sources articles:", e)
        return jsonify({"error": "Failed to fetch sources articles"}), 500

@app.route('/api/explore', methods=['GET'])
def explore_data():
    try:
        cur = g.db_cursor

        # Determine the start of the week (last Monday)
        today = datetime.today()
        last_monday = today - timedelta(days=today.weekday())
        first_day_of_month = datetime(today.year, today.month, 1)
        date_range_start = first_day_of_month
        date_range_end = today

        # Fetch top 3 politicians based on tag appearances this week
        cur.execute("""
            SELECT p.id, p.first_name, p.last_name, p.city, p.position, p.image_url, p.date_of_birth, COUNT(DISTINCT t.article_id) AS tag_count
            FROM politicians p
            JOIN tag_politician tp ON p.id = tp.politician_id
            JOIN tags t ON tp.tag_id = t.id
            JOIN articles a ON t.article_id = a.id
            WHERE a.published_date >= %s AND a.published_date <= %s
            GROUP BY p.id
            ORDER BY tag_count DESC
            LIMIT 3
        """, (date_range_start, date_range_end))
        top_politicians = cur.fetchall()

        politician_data = []
        for politician in top_politicians:
            cur.execute("""
                SELECT DISTINCT t.tag_text
                FROM tag_politician tp
                JOIN tags t ON tp.tag_id = t.id
                WHERE tp.politician_id = %s
            """, (politician[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            politician_dict = {
                'id': politician[0],
                'first_name': politician[1],
                'last_name': politician[2],
                'city': politician[3],
                'position': politician[4],
                'image_url': politician[5],
                'date_of_birth': politician[6],
                'tags': tags
            }
            politician_data.append(politician_dict)

        # Fetch top 3 cities based on tag appearances this week
        cur.execute("""
            SELECT c.id, c.name, c.description, c.image_url, c.candidates_for_mayor, c.mayor_id, COUNT(DISTINCT t.article_id) AS tag_count
            FROM cities c
            JOIN tag_city tc ON c.id = tc.city_id
            JOIN tags t ON tc.tag_id = t.id
            JOIN articles a ON t.article_id = a.id
            WHERE a.published_date >= %s AND a.published_date <= %s
            GROUP BY c.id
            ORDER BY tag_count DESC
            LIMIT 3
        """, (date_range_start, date_range_end))
        top_cities = cur.fetchall()

        city_data = []
        for city in top_cities:
            cur.execute("""
                SELECT DISTINCT t.tag_text
                FROM tag_city tc
                JOIN tags t ON tc.tag_id = t.id
                WHERE tc.city_id = %s
            """, (city[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            city_dict = {
                'id': city[0],
                'name': city[1],
                'description': city[2],
                'image_url': city[3],
                'candidates_for_mayor': city[4],
                'mayor_id': city[5],
                'tags': tags
            }
            city_data.append(city_dict)

        # Fetch top 3 political parties based on tag appearances this week
        cur.execute("""
            SELECT pp.id, pp.abbreviation, pp.full_name, pp.description, pp.image_url, COUNT(DISTINCT t.article_id) AS tag_count
            FROM political_parties pp
            JOIN tag_political_parties tpp ON pp.id = tpp.political_party_id
            JOIN tags t ON tpp.tag_id = t.id
            JOIN articles a ON t.article_id = a.id
            WHERE a.published_date >= %s AND a.published_date <= %s
            GROUP BY pp.id
            ORDER BY tag_count DESC
            LIMIT 3
        """, (date_range_start, date_range_end))
        top_parties = cur.fetchall()

        party_data = []
        for party in top_parties:
            cur.execute("""
                SELECT DISTINCT t.tag_text
                FROM tag_political_parties tpp
                JOIN tags t ON tpp.tag_id = t.id
                WHERE tpp.political_party_id = %s
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

        # Fetch top 3 sources based on articles published this week
        cur.execute("""
            SELECT s.id, s.name, s.image_url, COUNT(DISTINCT a.id) AS article_count
            FROM sources s
            JOIN articles a ON s.id = a.source
            WHERE a.published_date >= %s AND a.published_date <= %s
            GROUP BY s.id
            ORDER BY article_count DESC
            LIMIT 3
        """, (date_range_start, date_range_end))
        top_sources = cur.fetchall()

        source_data = []
        for source in top_sources:
            source_dict = {
                'id': source[0],
                'name': source[1],
                'image_url': source[2]
            }
            source_data.append(source_dict)

        return jsonify({
            'politicians': politician_data,
            'cities': city_data,
            'political_parties': party_data,
            'sources': source_data
        })

    except Exception as e:
        print("Error fetching explore data:", e)
        return jsonify({"error": "Failed to fetch explore data"}), 500

@app.route('/api/politicians', methods=['GET'])
def politicians_data():
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT id, first_name, last_name, city, position, image_url, date_of_birth
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
                'date_of_birth': politician[6],
                'tags': tags
            }
            politician_data.append(politician_dict)

        return jsonify({
            'politicians': politician_data
        })

    except Exception as e:
        print("Error fetching explore data:", e)
        return jsonify({"error": "Failed to fetch explore data"}), 500

@app.route('/api/cities', methods=['GET'])
def cities_data():
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT id, name, description, image_url, candidates_for_mayor, mayor_id
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
                'mayor_id': city[5],
                'tags': tags
            }
            city_data.append(city_dict)

        return jsonify({
            'cities': city_data
        })

    except Exception as e:
        print("Error fetching explore data:", e)
        return jsonify({"error": "Failed to fetch explore data"}), 500

@app.route('/api/alegeri/<category>', methods=['GET'])
def elections_data(category):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        cur = g.db_cursor

        if category.lower() == "toate alegerile":
            cur.execute("SELECT tag_text FROM tags WHERE id IN (SELECT tag_id FROM tag_election)")
        else:
            category_name = category.replace('-', ' ')
            cur.execute("SELECT id FROM elections WHERE name = %s", (category_name,))
            election_id = cur.fetchone()
            
            if not election_id:
                return jsonify({"error": "Invalid election category"}), 400
            
            election_id = election_id[0]

            # Fetch the tags associated with this election ID
            cur.execute("SELECT tag_text FROM tags WHERE id IN (SELECT tag_id FROM tag_election WHERE election_id = %s)", (election_id,))
        
        tags = [tag[0] for tag in cur.fetchall()]

        if not tags:
            return jsonify({"articles": [], "totalPages": 0})

        cur.execute("""
            SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion,
                   s.name AS source_name, s.image_url AS source_image_url
            FROM articles AS a
            JOIN tags AS t ON a.id = t.article_id
            JOIN sources AS s ON a.source = s.id
            WHERE t.tag_text = ANY(%s)
            GROUP BY a.id, s.id
            ORDER BY a.published_date DESC
            LIMIT %s OFFSET %s
        """, (tags, limit, offset))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("SELECT tag_text FROM tags WHERE article_id = %s", (article[0],))
            article_tags = [tag[0] for tag in cur.fetchall()]

            cur.execute("SELECT paragraph_text FROM article_paragraphs WHERE article_id = %s", (article[0],))
            article_text = [paragraph[0] for paragraph in cur.fetchall()]

            cur.execute("SELECT comment_text FROM comments WHERE article_id = %s", (article[0],))
            comments = [comment[0] for comment in cur.fetchall()]

            article_dict = {
                'id': article[0],
                'title': article[1],
                'url': article[2],
                'author': article[3],
                'published_date': article[4],
                'number_of_views': article[5],
                'tags': article_tags,
                'image_url': article[6],
                'article_text': article_text,
                'comments': comments,
                'emotion': article[8],
                'source_name': article[9],
                'source_image_url': article[10]
            }
            articles_list.append(article_dict)

        # Count total articles that match these tags
        cur.execute("""
            SELECT COUNT(DISTINCT a.id)
            FROM articles AS a
            JOIN tags AS t ON a.id = t.article_id
            WHERE t.tag_text = ANY(%s)
        """, (tags,))
        total_articles = cur.fetchone()[0]

        total_pages = (total_articles + limit - 1) // limit

        return jsonify({
            'articles': articles_list,
            'totalPages': total_pages
        })

    except Exception as e:
        print("Error fetching articles by category:", e)
        return jsonify({"error": "Failed to fetch articles by category"}), 500

@app.route('/api/favorites', methods=['POST'])
def manage_favorite():
    if g.db_cursor is None or g.db_conn is None:
        print("Database connection is not available")
        return jsonify({"error": "Database connection is not available"}), 500

    try:
        data = request.get_json()
        user_id = data['user_id']
        entity_id = data['entity_id']
        entity_type = data['entity_type']
        action = data['action']

        cur = g.db_cursor

        if action == 'add':
            cur.execute("""
                INSERT INTO favorites (user_id, entity_id, entity_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, entity_id, entity_type) DO NOTHING
            """, (user_id, entity_id, entity_type))
        elif action == 'remove':
            cur.execute("""
                DELETE FROM favorites
                WHERE user_id = %s AND entity_id = %s AND entity_type = %s
            """, (user_id, entity_id, entity_type))

        g.db_conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Error managing favorites:", e)
        return jsonify({"error": "Failed to manage favorites"}), 500

@app.route('/api/hidden_entities', methods=['POST'])
def manage_hidden_entities():
    if g.db_cursor is None or g.db_conn is None:
        print("Database connection is not available")
        return jsonify({"error": "Database connection is not available"}), 500

    try:
        data = request.get_json()
        user_id = data['user_id']
        entity_id = data['entity_id']
        entity_type = data['entity_type']
        action = data['action']  # 'hide' or 'unhide'

        cur = g.db_cursor

        if action == 'hide':
            cur.execute("""
                INSERT INTO hidden_entities (user_id, entity_id, entity_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, entity_id, entity_type) DO NOTHING
            """, (user_id, entity_id, entity_type))
        elif action == 'unhide':
            cur.execute("""
                DELETE FROM hidden_entities
                WHERE user_id = %s AND entity_id = %s AND entity_type = %s
            """, (user_id, entity_id, entity_type))

        g.db_conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Error managing hidden entities:", e)
        return jsonify({"error": "Failed to manage hidden entities"}), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    try:
        user_id = request.args.get('user_id')

        cur = g.db_cursor
        cur.execute("""
            SELECT entity_id, entity_type FROM favorites WHERE user_id = %s
        """, (user_id,))
        
        favorites = cur.fetchall()
        return jsonify(favorites)
    except Exception as e:
        print("Error fetching favorites:", e)
        return jsonify({"error": "Failed to fetch favorites"}), 500

@app.route('/api/hidden_entities', methods=['GET'])
def get_hidden_entities():
    try:
        user_id = request.args.get('user_id')

        cur = g.db_cursor
        cur.execute("""
            SELECT entity_id, entity_type FROM hidden_entities WHERE user_id = %s
        """, (user_id,))
        
        hidden_entities = cur.fetchall()
        return jsonify(hidden_entities)
    except Exception as e:
        print("Error fetching hidden entities:", e)
        return jsonify({"error": "Failed to fetch hidden entities"}), 500

@app.route('/api/my_interests', methods=['GET'])
def get_my_interests():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        if g.db_cursor is None or g.db_conn is None:
            return jsonify({"error": "Database connection is not established"}), 500

        cur = g.db_cursor

        # Fetch favorite entities
        cur.execute("""
            SELECT entity_id, entity_type
            FROM favorites
            WHERE user_id = %s
        """, (user_id,))
        favorite_entities = cur.fetchall()

        favorite_data = []
        entity_tags = {}

        for entity_id, entity_type in favorite_entities:
            if entity_type == 'politician':
                cur.execute("""
                    SELECT p.id, p.first_name, p.last_name, p.image_url, t.tag_text
                    FROM politicians p
                    LEFT JOIN tag_politician tp ON p.id = tp.politician_id
                    LEFT JOIN tags t ON tp.tag_id = t.id
                    WHERE p.id = %s
                """, (entity_id,))
                details = cur.fetchall()
                if details:
                    first_entry = details[0]
                    name = f"{first_entry[1]} {first_entry[2]}"
                    image_url = first_entry[3]
                    tags = [detail[4] for detail in details]
                    favorite_data.append({
                        'id': entity_id,
                        'type': entity_type,
                        'name': name,
                        'image_url': image_url
                    })
                    entity_tags[entity_id] = tags
            elif entity_type == 'city':
                cur.execute("""
                    SELECT c.id, c.name, c.image_url, t.tag_text
                    FROM cities c
                    LEFT JOIN tag_city tc ON c.id = tc.city_id
                    LEFT JOIN tags t ON tc.tag_id = t.id
                    WHERE c.id = %s
                """, (entity_id,))
                details = cur.fetchall()
                if details:
                    first_entry = details[0]
                    name = first_entry[1]
                    image_url = first_entry[2]
                    tags = [detail[3] for detail in details]
                    favorite_data.append({
                        'id': entity_id,
                        'type': entity_type,
                        'name': name,
                        'image_url': image_url
                    })
                    entity_tags[entity_id] = tags
            elif entity_type == 'political-party':
                cur.execute("""
                    SELECT pp.id, pp.abbreviation, pp.image_url, t.tag_text
                    FROM political_parties pp
                    LEFT JOIN tag_political_parties tpp ON pp.id = tpp.political_party_id
                    LEFT JOIN tags t ON tpp.tag_id = t.id
                    WHERE pp.id = %s
                """, (entity_id,))
                details = cur.fetchall()
                if details:
                    first_entry = details[0]
                    name = first_entry[1]
                    image_url = first_entry[2]
                    tags = [detail[3] for detail in details]
                    favorite_data.append({
                        'id': entity_id,
                        'type': entity_type,
                        'name': name,
                        'image_url': image_url
                    })
                    entity_tags[entity_id] = tags

        # Fetch articles related to favorite entities
        all_tags = [tag for tags in entity_tags.values() for tag in tags]
        if all_tags:
            cur.execute("""
                SELECT DISTINCT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion,
                                s.name AS source_name, s.image_url AS source_image_url
                FROM articles a
                JOIN tags t ON a.id = t.article_id
                JOIN sources AS s ON a.source = s.id
                WHERE t.tag_text = ANY(%s)
                GROUP BY a.id, s.id
                ORDER BY a.published_date DESC
            """, (all_tags,))
            related_articles = cur.fetchall()
        else:
            related_articles = []

        articles_data = []
        for article in related_articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            tags = [tag[0] for tag in cur.fetchall()]
            article_dict = {
                'id': article[0],
                'title': article[1],
                'url': article[2],
                'author': article[3],
                'published_date': article[4],
                'number_of_views': article[5],
                'tags': tags,
                'image_url': article[6],
                'emotion': article[8],
                'source_name': article[9],
                'source_image_url': article[10]
            }
            articles_data.append(article_dict)

        return jsonify({
            'favorite_entities': favorite_data,
            'related_articles': articles_data
        })

    except Exception as e:
        print("Error fetching my interests:", e)
        return jsonify({"error": "Failed to fetch my interests"}), 500


### MY INTERESTS SUGGESTIONS ###
@app.route('/api/random-suggestions', methods=['GET'])
def random_suggestions():
    if g.db_cursor is None or g.db_conn is None:
        return jsonify({"error": "Database connection is not available"}), 500

    try:
        cur = g.db_cursor

        # Fetch random cities (only need one)
        cur.execute("SELECT id, name, image_url, 'city' as type FROM cities ORDER BY RANDOM() LIMIT 1")
        city = cur.fetchone()

        # Fetch random politicians
        cur.execute("SELECT id, first_name || ' ' || last_name as name, image_url, 'politician' as type FROM politicians ORDER BY RANDOM() LIMIT 5")
        politicians = cur.fetchall()

        # Fetch random political parties
        cur.execute("SELECT id, abbreviation as name, image_url, 'political-party' as type FROM political_parties ORDER BY RANDOM() LIMIT 5")
        political_parties = cur.fetchall()

        # Combine politicians and political parties
        combined = politicians + political_parties

        # Select 4 random politicians or political parties
        random_combined = random.sample(combined, 4)

        # Ensure the city is included in the suggestions
        random_suggestions = [city] + random_combined

        # Convert to dictionary format
        suggestions_dict = [
            {"id": entity[0], "name": entity[1], "image_url": entity[2], "type": entity[3]}
            for entity in random_suggestions
        ]

        return jsonify(suggestions_dict)
    except Exception as e:
        print("Error fetching random suggestions:", e)
        return jsonify({"error": "Failed to fetch random suggestions"}), 500


### SEARCH SUGGESTIONS ###

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

def get_articles_by_source_id(source_id):
    try:
        cur = g.db_cursor
        cur.execute("""
            SELECT id, title, url, author, published_date, number_of_views, image_url, source
            FROM articles
            WHERE source = %s
            ORDER BY published_date ASC
        """, (source_id,))
        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            article_dict = {
                'id': article[0],
                'title': article[1],
                'url': article[2],
                'author': article[3],
                'published_date': article[4],
                'number_of_views': article[5],
                'image_url': article[6],
                'source': article[7]
            }
            articles_list.append(article_dict)

        return articles_list

    except Exception as e:
        print("Error fetching articles for source:", e)
        return []

@app.route('/api/suggestions')
def get_suggestions():
    query = request.args.get('query')
    
    # Querying entities
    politician_suggestions = query_politicians(query)
    political_parties_suggestions = query_political_parties(query)
    cities_suggestions = query_cities(query)
    elections_suggestions = query_elections(query)
    sources_suggestions = query_sources(query)
    
    suggestions_from_entities = (politician_suggestions + political_parties_suggestions + 
                                 cities_suggestions + elections_suggestions + sources_suggestions)
    
    if suggestions_from_entities:
        # Handling case when only one suggestion is found
        if len(suggestions_from_entities) == 1:
            single_suggestion = suggestions_from_entities[0]
            articles = []
            
            # Fetching articles based on the single suggestion category
            if single_suggestion['category'] == 'Politician':
                articles = get_articles_by_politician_id(single_suggestion['id'])
            elif single_suggestion['category'] == 'Partid politic':
                articles = get_articles_by_political_party_id(single_suggestion['id'])
            elif single_suggestion['category'] == 'Oraș':
                articles = get_articles_by_city_id(single_suggestion['id'])
            elif single_suggestion['category'] == 'Sursă':
                articles = get_articles_by_source_id(single_suggestion['id'])
            
            # Creating article suggestions
            article_suggestions = [{
                'id':  article['id'],
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

        return jsonify(suggestions_from_entities[:5])

    # Querying articles if no entity suggestions are found
    article_suggestions = query_articles(query)
    if article_suggestions:
        return jsonify(article_suggestions[:5])
    
    # Querying tags if no entity or article suggestions are found
    tags_suggestions = query_tags(query)
    return jsonify(tags_suggestions[:5])


### SEARCH RESULTS ###
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit

    results = {
        "politicians": query_politicians(query),
        "political_parties": query_political_parties(query),
        "cities": query_cities(query),
        "elections": query_elections(query),
        "sources": query_sources(query),
    }

    # Combine all entities into a single list
    entities = []
    for category in ["politicians", "political_parties", "cities", "elections", "sources"]:
        if results[category]:
            entities.extend(results[category])

    # Check if sources are present
    if results["sources"]:
        for source in results["sources"]:
            articles = query_articles_by_source(source["name"])
            if articles:
                entities.extend(articles)
    else:
        articles = query_articles(query)
        if articles:
            entities.extend(articles)

    total_results = len(entities)

    # Calculate total number of pages based on the combined results
    total_pages = (total_results + limit - 1) // limit

    # Paginate the combined results
    paginated_results = entities[offset:offset + limit]

    response = {
        "results": paginated_results,
        "totalPages": total_pages,
        "totalResults": total_results,
        "currentPage": page
    }

    print(f"Page: {page}, Limit: {limit}, Offset: {offset}, Total Results: {total_results}, Total Pages: {total_pages}")

    return jsonify(response)



### ENTITIES PAGES ###

@app.route('/api/politician/<int:id>', methods=['GET'])
def get_politician(id):
    try:
        user_id = request.args.get('user_id')
        
        cur = g.db_cursor
        fields = """
            p.id, p.first_name, p.last_name, p.city, p.image_url, p.position, p.description, p.political_party_position,
            pp.id as political_party_id, pp.abbreviation as political_party_abbreviation, pp.image_url as political_party_image_url,
            p.date_of_birth, 'politician' as entity_type
        """
        cur.execute(f"""
            SELECT {fields}
            FROM politicians p
            LEFT JOIN political_parties pp ON p.political_party_id = pp.id
            WHERE p.id = %s
        """, (id,))
        politician = cur.fetchone()
        
        if politician:
            # Convert the tuple to a dictionary
            politician_dict = dict(zip([desc[0] for desc in cur.description], politician))
            
            date_of_birth = politician_dict['date_of_birth']
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            politician_dict['age'] = age

            # Fetch tags associated with the politician
            cur.execute("SELECT t.tag_text FROM tag_politician tp JOIN tags t ON tp.tag_id = t.id WHERE tp.politician_id = %s", (id,))
            tags = [tag[0] for tag in cur.fetchall()]
            politician_dict['tags'] = tags

            if tags:
                tag_texts_str = "','".join(tags)  # Create a comma-separated string of tag texts

                # Fetch article counts
                cur.execute(f"""
                    WITH filtered_articles AS (
                        SELECT DISTINCT a.id AS article_id, a.emotion
                        FROM articles a
                        JOIN tags t ON a.id = t.article_id
                        WHERE t.tag_text IN ('{tag_texts_str}')
                    )
                    SELECT 
                        COUNT(article_id) AS total_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Positive' THEN article_id END) AS positive_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Negative' THEN article_id END) AS negative_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Neutral' THEN article_id END) AS neutral_articles
                    FROM filtered_articles
                """)
                article_counts = cur.fetchone()
                
                politician_dict['total_articles'] = article_counts[0]
                politician_dict['positive_articles'] = article_counts[1]
                politician_dict['negative_articles'] = article_counts[2]
                politician_dict['neutral_articles'] = article_counts[3]
            else:
                politician_dict['total_articles'] = 0
                politician_dict['positive_articles'] = 0
                politician_dict['negative_articles'] = 0
                politician_dict['neutral_articles'] = 0
            
            # Check if the entity is a favorite
            if user_id:
                cur.execute("SELECT 1 FROM favorites WHERE user_id = %s AND entity_id = %s AND entity_type = 'politician'", (user_id, id))
                is_favorite = cur.fetchone() is not None
                politician_dict['isFavorite'] = is_favorite
            else:
                politician_dict['isFavorite'] = None

            return jsonify(politician_dict)
        else:
            return jsonify({"error": "Politician not found"}), 404
    except Exception as e:
        print("Error fetching politician:", e)
        return jsonify({"error": "Failed to fetch politician data"}), 500

@app.route('/api/political-party/<int:id>', methods=['GET'])
def get_political_party(id):
    try:
        user_id = request.args.get('user_id')
        
        cur = g.db_cursor
        fields = """
            pp.id, pp.full_name, pp.abbreviation, pp.description, pp.image_url, pp.founded_year, pp.position, pp.ideology, pp.president_id, 'political-party' as entity_type
        """
        cur.execute(f"""
            SELECT {fields}
            FROM political_parties pp
            WHERE pp.id = %s
        """, (id,))
        party = cur.fetchone()
        
        if party:
            # Convert the tuple to a dictionary
            party_dict = dict(zip([desc[0] for desc in cur.description], party))
            
            # Fetch tags associated with the political party
            cur.execute("SELECT t.tag_text FROM tag_political_parties tpp JOIN tags t ON tpp.tag_id = t.id WHERE tpp.political_party_id = %s", (id,))
            tags = [tag[0] for tag in cur.fetchall()]
            party_dict['tags'] = tags

            if tags:
                tag_texts_str = "','".join(tags)  # Create a comma-separated string of tag texts

                # Fetch article counts
                cur.execute(f"""
                    WITH filtered_articles AS (
                        SELECT DISTINCT a.id AS article_id, a.emotion
                        FROM articles a
                        JOIN tags t ON a.id = t.article_id
                        WHERE t.tag_text IN ('{tag_texts_str}')
                    )
                    SELECT 
                        COUNT(article_id) AS total_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Positive' THEN article_id END) AS positive_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Negative' THEN article_id END) AS negative_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Neutral' THEN article_id END) AS neutral_articles
                    FROM filtered_articles
                """)
                article_counts = cur.fetchone()
                
                party_dict['total_articles'] = article_counts[0]
                party_dict['positive_articles'] = article_counts[1]
                party_dict['negative_articles'] = article_counts[2]
                party_dict['neutral_articles'] = article_counts[3]
            else:
                party_dict['total_articles'] = 0
                party_dict['positive_articles'] = 0
                party_dict['negative_articles'] = 0
                party_dict['neutral_articles'] = 0
            
            # Check if the entity is a favorite
            if user_id:
                cur.execute("SELECT 1 FROM favorites WHERE user_id = %s AND entity_id = %s AND entity_type = 'political-party'", (user_id, id))
                is_favorite = cur.fetchone() is not None
                party_dict['isFavorite'] = is_favorite
            else:
                party_dict['isFavorite'] = None

            return jsonify(party_dict)
        else:
            return jsonify({"error": "Political party not found"}), 404
    except Exception as e:
        print("Error fetching political party:", e)
        return jsonify({"error": "Failed to fetch political party data"}), 500

@app.route('/api/city/<int:id>', methods=['GET'])
def get_city(id):
    try:
        user_id = request.args.get('user_id')

        cur = g.db_cursor
        
        fields = """
            c.id, c.name, c.population, c.image_url, c.description, c.mayor_id, 'city' as entity_type
        """
        cur.execute(f"""
            SELECT {fields}
            FROM cities c
            WHERE c.id = %s
        """, (id,))
        city = cur.fetchone()

        if city:
            city_dict = dict(zip([desc[0] for desc in cur.description], city))
            
            # Fetch mayor_id details from politicians table
            mayor_id = city_dict.get('mayor_id')
            if mayor_id:
                cur.execute("""
                    SELECT id, first_name, last_name, image_url
                    FROM politicians
                    WHERE id = %s
                """, (mayor_id,))
                mayor = cur.fetchone()
                if mayor:
                    mayor_dict = {
                        'id': mayor[0],
                        'name': f"{mayor[1]} {mayor[2]}",
                        'image_url': mayor[3]
                    }
                    city_dict['mayor'] = mayor_dict

            cur.execute("SELECT t.tag_text FROM tag_city tc JOIN tags t ON tc.tag_id = t.id WHERE tc.city_id = %s", (id,))
            tags = [tag[0] for tag in cur.fetchall()]
            city_dict['tags'] = tags
            
            if tags:
                tag_texts_str = "','".join(tags)  # Create a comma-separated string of tag texts

                # Fetch article counts
                cur.execute(f"""
                    WITH filtered_articles AS (
                        SELECT DISTINCT a.id AS article_id, a.emotion
                        FROM articles a
                        JOIN tags t ON a.id = t.article_id
                        WHERE t.tag_text IN ('{tag_texts_str}')
                    )
                    SELECT 
                        COUNT(article_id) AS total_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Positive' THEN article_id END) AS positive_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Negative' THEN article_id END) AS negative_articles,
                        COUNT(DISTINCT CASE WHEN emotion = 'Neutral' THEN article_id END) AS neutral_articles
                    FROM filtered_articles
                """)
                article_counts = cur.fetchone()
                
                city_dict['total_articles'] = article_counts[0]
                city_dict['positive_articles'] = article_counts[1]
                city_dict['negative_articles'] = article_counts[2]
                city_dict['neutral_articles'] = article_counts[3]
            else:
                city_dict['total_articles'] = 0
                city_dict['positive_articles'] = 0
                city_dict['negative_articles'] = 0
                city_dict['neutral_articles'] = 0
            
            if user_id:
                cur.execute("SELECT 1 FROM favorites WHERE user_id = %s AND entity_id = %s AND entity_type = 'city'", (user_id, id))
                is_favorite = cur.fetchone() is not None
                city_dict['isFavorite'] = is_favorite
            else:
                city_dict['isFavorite'] = None

            return jsonify(city_dict)
        else:
            return jsonify({"error": "City not found"}), 404
    except Exception as e:
        print("Error fetching city:", e)
        return jsonify({"error": "Failed to fetch city data"}), 500

@app.route('/api/source/<int:id>', methods=['GET'])
def get_source(id):
    try:
        cur = g.db_cursor

        # Fetch source details
        cur.execute("SELECT * FROM sources WHERE id = %s", (id,))
        source = cur.fetchone()

        if not source:
            return jsonify({"error": "Source not found"}), 404

        source_dict = dict(zip([desc[0] for desc in cur.description], source))

        # Fetch total number of articles for the source
        cur.execute("""
            SELECT COUNT(*) AS total_articles
            FROM articles
            WHERE source = %s
        """, (id,))
        total_articles_result = cur.fetchone()
        total_articles = total_articles_result[0] if total_articles_result else 0

        source_dict['total_articles'] = total_articles

        # Fetch counts of positive, negative, and neutral articles for the source
        cur.execute("""
            SELECT
                SUM(CASE WHEN emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                SUM(CASE WHEN emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                SUM(CASE WHEN emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
            FROM articles
            WHERE source = %s
        """, (id,))
        emotion_counts = cur.fetchone()

        if emotion_counts:
            source_dict['positive_articles'] = emotion_counts[0] if emotion_counts[0] else 0
            source_dict['negative_articles'] = emotion_counts[1] if emotion_counts[1] else 0
            source_dict['neutral_articles'] = emotion_counts[2] if emotion_counts[2] else 0
        else:
            source_dict['positive_articles'] = 0
            source_dict['negative_articles'] = 0
            source_dict['neutral_articles'] = 0

        return jsonify(source_dict)

    except psycopg2.Error as e:
        print("Error fetching source details:", e)
        return jsonify({"error": "Failed to fetch source details"}), 500

    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500

@app.route('/api/articles/<entity_type>/<int:entity_id>', methods=['GET'])
def get_articles_by_entity(entity_type, entity_id):
    try:
        cur = g.db_cursor
        if entity_type not in ['politician', 'political-party', 'city', 'source']:
            return jsonify({"error": "Invalid entity type"}), 400

        tags = []
        if entity_type == 'politician':
            cur.execute("SELECT tag_text FROM tag_politician JOIN tags ON tag_politician.tag_id = tags.id WHERE politician_id = %s", (entity_id,))
            tags = [tag[0] for tag in cur.fetchall()]
        elif entity_type == 'political-party':
            cur.execute("SELECT tag_text FROM tag_political_parties JOIN tags ON tag_political_parties.tag_id = tags.id WHERE political_party_id = %s", (entity_id,))
            tags = [tag[0] for tag in cur.fetchall()]
        elif entity_type == 'city':
            cur.execute("SELECT tag_text FROM tag_city JOIN tags ON tag_city.tag_id = tags.id WHERE city_id = %s", (entity_id,))
            tags = [tag[0] for tag in cur.fetchall()]

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
        offset = (page - 1) * limit

        if entity_type == 'source':
            cur.execute("""
                SELECT COUNT(*)
                FROM articles
                WHERE source = %s
            """, (entity_id,))
            total_articles = cur.fetchone()[0]

            cur.execute("""
                SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion,
                    s.name AS source_name, s.image_url AS source_image_url
                FROM articles AS a
                JOIN sources AS s ON a.source = s.id
                WHERE a.source = %s
                ORDER BY a.published_date DESC
                LIMIT %s OFFSET %s
            """, (entity_id, limit, offset))
        else:
            if tags:
                cur.execute("""
                    SELECT COUNT(*)
                    FROM articles AS a
                    JOIN tags AS t ON a.id = t.article_id
                    WHERE t.tag_text IN %s
                """, (tuple(tags),))
                total_articles = cur.fetchone()[0]

                cur.execute("""
                    SELECT a.id, a.title, a.url, a.author, a.published_date, a.number_of_views, a.image_url, a.source, a.emotion,
                        s.name AS source_name, s.image_url AS source_image_url
                    FROM articles AS a
                    JOIN sources AS s ON a.source = s.id
                    JOIN tags AS t ON a.id = t.article_id
                    WHERE t.tag_text IN %s
                    GROUP BY a.id, s.id
                    ORDER BY a.published_date DESC
                    LIMIT %s OFFSET %s
                """, (tuple(tags), limit, offset))
            else:
                return jsonify({"total": 0, "articles": []})

        articles = cur.fetchall()

        articles_list = []
        for article in articles:
            cur.execute("""
                SELECT tag_text
                FROM tags
                WHERE article_id = %s
            """, (article[0],))
            article_tags = [tag[0] for tag in cur.fetchall()]

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
                'tags': article_tags,
                'image_url': article[6],
                'article_text': article_text,
                'comments': comments,
                'source': article[7],
                'emotion': article[8],
                'source_name': article[9],
                'source_image_url': article[10]
            }
            articles_list.append(article_dict)

        return jsonify({"total": total_articles, "articles": articles_list})
    except Exception as e:
        print("Error fetching articles:", e)
        return jsonify({"error": "Failed to fetch articles"}), 500



### LOGIN ###

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
        user_data = {}

        if session_token:
            cur = g.db_cursor
            cur.execute("SELECT id, email FROM users WHERE session_token = %s", (session_token,))
            user = cur.fetchone()

            if user:
                user_data = {
                    "id": user[0],
                    "email": user[1],
                }
                return jsonify({"message": "You are authorized to access this resource", "user": user_data}), 200

        # If no session token or user is not found
        return jsonify({"message": "You are not logged in", "user": user_data}), 200

    except Exception as e:
        print("Error accessing protected route:", e)
        return jsonify({"error": "Failed to access protected route"}), 500
    



### SOURCE CHARTS ###

@app.route('/api/articles/emotion-distribution/source/<int:source_id>', methods=['GET'])
def get_emotion_distribution_for_source(source_id):
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = """
            SELECT a.emotion, COUNT(*)
            FROM articles AS a
            WHERE a.source = %s
        """
        params = [source_id]

        if start_date:
            query += " AND DATE(a.published_date) >= %s"
            params.append(start_date)

        if end_date:
            query += " AND DATE(a.published_date) <= %s"
            params.append(end_date)

        query += " GROUP BY a.emotion"
        cur = g.db_cursor
        cur.execute(query, tuple(params))
        results = cur.fetchall()

        emotion_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        for emotion, count in results:
            emotion_distribution[emotion.lower()] = count

        return jsonify(emotion_distribution)

    except Exception as e:
        print("Error fetching emotion distribution for source:", e)
        return jsonify({"error": "Failed to fetch emotion distribution for source"}), 500

@app.route('/api/articles/emotion-distribution-over-time/source/<int:source_id>', methods=['GET'])
def get_emotion_distribution_for_source_over_time(source_id):
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = """
            SELECT DATE(a.published_date) as date, a.emotion, COUNT(*) as count
            FROM articles AS a
            WHERE a.source = %s
        """
        params = [source_id]

        if start_date:
            query += " AND DATE(a.published_date) >= %s"
            params.append(start_date)

        if end_date:
            query += " AND DATE(a.published_date) <= %s"
            params.append(end_date)

        query += " GROUP BY DATE(a.published_date), a.emotion"
        cur = g.db_cursor
        cur.execute(query, tuple(params))
        results = cur.fetchall()

        # Process results into a format suitable for the chart
        emotion_distribution = {}
        for date, emotion, count in results:
            if date not in emotion_distribution:
                emotion_distribution[date] = {'date': date, 'positive': 0, 'negative': 0, 'neutral': 0}
            emotion_distribution[date][emotion.lower()] = count

        return jsonify(list(emotion_distribution.values()))

    except Exception as e:
        print("Error fetching emotion distribution for source:", e)
        return jsonify({"error": "Failed to fetch emotion distribution for source"}), 500

@app.route('/api/articles/hourly-distribution/source/<int:source_id>', methods=['GET'])
def get_hourly_distribution_for_source(source_id):
    try:
        cur = g.db_cursor

        query = """
            SELECT EXTRACT(HOUR FROM a.published_date) as hour, COUNT(*) as count
            FROM articles AS a
            WHERE a.source = %s
            GROUP BY EXTRACT(HOUR FROM a.published_date)
        """
        params = [source_id]

        cur.execute(query, tuple(params))
        results = cur.fetchall()

        hourly_distribution = [0] * 24
        for hour, count in results:
            hourly_distribution[int(hour)] = count

        return jsonify(hourly_distribution)

    except Exception as e:
        print("Error fetching hourly distribution for source:", e)
        return jsonify({"error": "Failed to fetch hourly distribution for source"}), 500
    
@app.route('/api/articles/counts-today/source/<int:source_id>', methods=['GET'])
def get_article_counts_for_source_today(source_id):
    try:
        today_date = datetime.now().date()
        cur = g.db_cursor
        
        total_query = """
            SELECT COUNT(*) FROM articles
            WHERE source = %s AND DATE(published_date) = %s
        """
        cur.execute(total_query, (source_id, today_date))
        total_count = cur.fetchone()[0]

        # Query to get counts by emotion
        emotion_query = """
            SELECT emotion, COUNT(*) FROM articles
            WHERE source = %s AND DATE(published_date) = %s
            GROUP BY emotion
        """
        cur.execute(emotion_query, (source_id, today_date))
        emotion_counts = cur.fetchall()

        counts = {
            'total': total_count,
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        for emotion, count in emotion_counts:
            counts[emotion.lower()] = count

        return jsonify(counts)

    except Exception as e:
        print("Error fetching article counts for source:", e)
        return jsonify({"error": "Failed to fetch article counts for source"}), 500

@app.route('/api/sources/favorite-entities/<int:source_id>', methods=['GET'])
def get_favorite_entities(source_id):
    try:
        cur = g.db_cursor

        cur.execute("""
            SELECT entity_id, entity_type, entity_name, image_url, COUNT(DISTINCT article_id) AS total_count
            FROM (
                SELECT p.id AS entity_id, 'politician' AS entity_type, CONCAT(p.first_name, ' ', p.last_name) AS entity_name, p.image_url, t.article_id
                FROM politicians p
                JOIN tag_politician tp ON p.id = tp.politician_id
                JOIN tags t ON tp.tag_id = t.id
                JOIN articles a ON t.article_id = a.id
                WHERE a.source = %s

                UNION ALL

                SELECT pp.id AS entity_id, 'political-party' AS entity_type, pp.abbreviation AS entity_name, pp.image_url, t.article_id
                FROM political_parties pp
                JOIN tag_political_parties tpp ON pp.id = tpp.political_party_id
                JOIN tags t ON tpp.tag_id = t.id
                JOIN articles a ON t.article_id = a.id
                WHERE a.source = %s

                UNION ALL

                SELECT c.id AS entity_id, 'city' AS entity_type, c.name AS entity_name, c.image_url, t.article_id
                FROM cities c
                JOIN tag_city tc ON c.id = tc.city_id
                JOIN tags t ON tc.tag_id = t.id
                JOIN articles a ON t.article_id = a.id
                WHERE a.source = %s
            ) AS entity_counts
            GROUP BY entity_id, entity_type, entity_name, image_url
            ORDER BY total_count DESC
            LIMIT 5
        """, (source_id, source_id, source_id))
        
        top_entities = cur.fetchall()

        # Prepare response
        response = {
            'source_id': source_id,
            'top_entities': [{'entity_id': row[0], 'entity_type': row[1], 'entity_name': row[2], 'image_url': row[3], 'total_count': row[4]} for row in top_entities]
        }

        return jsonify(response)

    except psycopg2.Error as e:
        print("Error fetching favorite entities:", e)
        return jsonify({"error": "Failed to fetch favorite entities"}), 500

@app.route('/api/top-entities/<int:source_id>', methods=['GET'])
def get_top_entities(source_id):
    try:
        cur = g.db_cursor

        # SQL query to retrieve the percentages of positive, negative, and neutral articles for each entity
        query = """
            WITH entity_articles AS (
                SELECT p.id AS entity_id, 'politician' AS entity_type, CONCAT(p.first_name, ' ', p.last_name) AS entity_name,
                       p.image_url, 
                       COUNT(a.id) AS total_articles,
                       SUM(CASE WHEN a.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                       SUM(CASE WHEN a.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                       SUM(CASE WHEN a.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
                FROM politicians p
                JOIN tag_politician tp ON p.id = tp.politician_id
                JOIN tags t ON tp.tag_id = t.id
                JOIN articles a ON t.article_id = a.id
                WHERE a.source = %s
                GROUP BY p.id, p.first_name, p.last_name, p.image_url

                UNION ALL

                SELECT pp.id AS entity_id, 'political-party' AS entity_type, pp.abbreviation AS entity_name,
                       pp.image_url, 
                       COUNT(a.id) AS total_articles,
                       SUM(CASE WHEN a.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                       SUM(CASE WHEN a.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                       SUM(CASE WHEN a.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
                FROM political_parties pp
                JOIN tag_political_parties tpp ON pp.id = tpp.political_party_id
                JOIN tags t ON tpp.tag_id = t.id
                JOIN articles a ON t.article_id = a.id
                WHERE a.source = %s
                GROUP BY pp.id, pp.abbreviation, pp.image_url

                UNION ALL

                SELECT c.id AS entity_id, 'city' AS entity_type, c.name AS entity_name,
                       c.image_url, 
                       COUNT(a.id) AS total_articles,
                       SUM(CASE WHEN a.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                       SUM(CASE WHEN a.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                       SUM(CASE WHEN a.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
                FROM cities c
                JOIN tag_city tc ON c.id = tc.city_id
                JOIN tags t ON tc.tag_id = t.id
                JOIN articles a ON t.article_id = a.id
                WHERE a.source = %s
                GROUP BY c.id, c.name, c.image_url
            )

            SELECT entity_id, entity_type, entity_name, image_url,
                   (positive_articles::decimal / total_articles * 100) AS positive_percentage,
                   (negative_articles::decimal / total_articles * 100) AS negative_percentage,
                   (neutral_articles::decimal / total_articles * 100) AS neutral_percentage
            FROM entity_articles
            WHERE total_articles > 0
            ORDER BY positive_percentage DESC
            LIMIT 3
        """

        cur.execute(query, (source_id, source_id, source_id))
        rows = cur.fetchall()

        # Prepare response data
        top_entities = []
        for row in rows:
            entity_id, entity_type, entity_name, image_url, positive_percentage, negative_percentage, neutral_percentage = row
            top_entities.append({
                'entity_id': entity_id,
                'entity_type': entity_type,
                'entity_name': entity_name,
                'image_url': image_url,
                'positive_percentage': positive_percentage,
                'negative_percentage': negative_percentage,
                'neutral_percentage': neutral_percentage
            })

        return jsonify({'top_entities': top_entities})

    except psycopg2.Error as e:
        print("Error fetching top entities:", e)
        return jsonify({"error": "Failed to fetch top entities"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500


### POLITICIAN CHARTS ###
    
@app.route('/api/politician-sources-count/<int:politician_id>', methods=['GET'])
def get_sources_by_politician_id(politician_id):
    try:
        cur = g.db_cursor
        
        cur.execute("""
            WITH unique_articles AS (
                SELECT DISTINCT a.id, a.source
                FROM articles AS a
                JOIN tags AS t ON a.id = t.article_id
                WHERE t.tag_text IN (
                    SELECT tag_text
                    FROM tag_politician
                    JOIN tags ON tag_politician.tag_id = tags.id
                    WHERE politician_id = %s
                )
            )
            SELECT s.id, s.name, s.image_url, COUNT(ua.id) AS article_count
            FROM unique_articles AS ua
            JOIN sources AS s ON ua.source = s.id
            GROUP BY s.id
            ORDER BY article_count DESC
        """, (politician_id,))
        sources = cur.fetchall()

        sources_list = []
        for source in sources:
            source_dict = {
                'id': source[0],
                'name': source[1],
                'image_url': source[2],
                'article_count': source[3]
            }
            sources_list.append(source_dict)

        return jsonify(sources_list)

    except Exception as e:
        print("Error fetching sources for politician:", e)
        return jsonify({"error": "Failed to fetch sources for politician"}), 500

@app.route('/api/politician-articles-distribution/<int:politician_id>', methods=['GET'])
def get_articles_distribution(politician_id):
    try:
        cur = g.db_cursor

        today = datetime.today()
        date_7_days_ago = today - timedelta(days=7)

        cur.execute("""
            SELECT 
                DATE(a.published_date) AS publish_date,
                SUM(CASE WHEN a.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_count,
                SUM(CASE WHEN a.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_count,
                SUM(CASE WHEN a.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_count,
                COUNT(a.id) AS total_count
            FROM articles AS a
            JOIN tags AS t ON a.id = t.article_id
            WHERE t.tag_text IN (
                SELECT tag_text
                FROM tag_politician
                JOIN tags ON tag_politician.tag_id = tags.id
                WHERE politician_id = %s
            ) AND a.published_date BETWEEN %s AND %s
            GROUP BY DATE(a.published_date)
            ORDER BY publish_date
        """, (politician_id, date_7_days_ago, today))
        
        articles = cur.fetchall()

        dates = []
        positive_counts = []
        negative_counts = []
        neutral_counts = []
        total_counts = []

        for article in articles:
            dates.append(article[0].strftime('%Y-%m-%d'))
            positive_counts.append(article[1])
            negative_counts.append(article[2])
            neutral_counts.append(article[3])
            total_counts.append(article[4])

        return jsonify({
            'dates': dates,
            'positive_counts': positive_counts,
            'negative_counts': negative_counts,
            'neutral_counts': neutral_counts,
            'total_counts': total_counts
        })

    except Exception as e:
        print("Error fetching articles distribution for politician:", e)
        return jsonify({"error": "Failed to fetch articles distribution for politician"}), 500



