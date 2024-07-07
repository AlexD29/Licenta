# stats_routes.py
from flask import Blueprint, jsonify, request, g
from datetime import datetime, timedelta
from collections import defaultdict
import re
import psycopg2

from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

nlp = spacy.load("ro_core_news_sm")

statistics_bp = Blueprint('statistics', __name__)


### HOME PAGE ###

@statistics_bp.route('/api/random-fact', methods=['GET'])
def random_fact():
    try:
        cur = g.db_cursor

        # Query to select a random fact using ORDER BY RANDOM() LIMIT 1
        cur.execute("SELECT text FROM facts ORDER BY RANDOM() LIMIT 1")

        # Fetch the random fact
        random_fact = cur.fetchone()[0]

        # Close cursor and connection
        cur.close()

        return jsonify({'fact': random_fact})

    except psycopg2.Error as e:
        print("Error fetching random fact from PostgreSQL:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

@statistics_bp.route('/api/articles/today', methods=['GET'])
def get_today_articles_summary():
    try:
        today_date = datetime.now().date()
        cur = g.db_cursor

        cur.execute("""
            SELECT 
                COUNT(*) AS total_articles,
                COUNT(CASE WHEN a.emotion = 'Positive' THEN 1 END) AS positive_articles,
                COUNT(CASE WHEN a.emotion = 'Negative' THEN 1 END) AS negative_articles,
                COUNT(CASE WHEN a.emotion = 'Neutral' THEN 1 END) AS neutral_articles
            FROM articles AS a
            WHERE DATE(a.published_date) = %s
        """, (today_date,))
        
        result = cur.fetchone()
        summary = {
            'total_articles': result[0],
            'positive_articles': result[1],
            'negative_articles': result[2],
            'neutral_articles': result[3]
        }

        return jsonify(summary)
    except Exception as e:
        print("Error fetching today's articles summary:", e)
        return jsonify({"error": "Failed to fetch today's articles summary"}), 500

@statistics_bp.route('/api/top-politicians', methods=['GET'])
def get_top_politicians():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Use current date if start_date or end_date is not provided
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, microseconds=-1)

        cur = g.db_cursor

        # Step 1: Get the tag_text of tags associated with politicians
        politician_tag_texts_query = """
            SELECT DISTINCT t.tag_text
            FROM tag_politician tp
            JOIN tags t ON tp.tag_id = t.id
        """

        cur.execute(politician_tag_texts_query)
        politician_tag_texts = [row[0] for row in cur.fetchall()]

        if not politician_tag_texts:
            return jsonify({'top_politicians': []})

        # Step 2: Find all tags that have the same tag_text as those associated with politicians
        tags_query = """
            SELECT id
            FROM tags
            WHERE tag_text = ANY(%s)
        """

        cur.execute(tags_query, (politician_tag_texts,))
        tag_ids = [row[0] for row in cur.fetchall()]

        if not tag_ids:
            return jsonify({'top_politicians': []})

        # Step 3: Retrieve articles associated with these tags and calculate statistics
        query = """
            WITH unique_politician_articles AS (
                SELECT
                    a.id AS article_id,
                    p.id AS politician_id,
                    p.image_url,
                    a.emotion
                FROM articles a
                JOIN tags t ON a.id = t.article_id
                JOIN (
                    SELECT DISTINCT tp.politician_id, t.tag_text
                    FROM tag_politician tp
                    JOIN tags t ON tp.tag_id = t.id
                ) tp ON t.tag_text = tp.tag_text
                JOIN politicians p ON tp.politician_id = p.id
                WHERE a.published_date BETWEEN %s AND %s
                  AND t.id = ANY(%s)
                GROUP BY a.id, p.id, p.image_url, a.emotion
            )

            SELECT
                p.id AS politician_id,
                CONCAT(p.first_name, ' ', p.last_name) AS politician_name,
                p.image_url,
                COUNT(DISTINCT upa.article_id) AS total_articles,
                SUM(CASE WHEN upa.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                SUM(CASE WHEN upa.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                SUM(CASE WHEN upa.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
            FROM unique_politician_articles upa
            JOIN politicians p ON upa.politician_id = p.id
            GROUP BY p.id, p.first_name, p.last_name, p.image_url
            ORDER BY total_articles DESC
            LIMIT 3
        """

        cur.execute(query, (start_date, end_date, tag_ids))
        rows = cur.fetchall()

        # Prepare response data
        top_politicians = []
        for row in rows:
            politician_id, politician_name, image_url, total_articles, positive_articles, negative_articles, neutral_articles = row
            top_politicians.append({
                'politician_id': politician_id,
                'politician_name': politician_name,
                'image_url': image_url,
                'total_articles': total_articles,
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'neutral_articles': neutral_articles
            })

        return jsonify({'top_politicians': top_politicians})

    except psycopg2.Error as e:
        print("Error fetching top politicians:", e)
        return jsonify({"error": "Failed to fetch top politicians"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500

@statistics_bp.route('/api/top-political-parties', methods=['GET'])
def get_top_political_parties():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Use current date if start_date or end_date is not provided
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, microseconds=-1)

        cur = g.db_cursor

        # Step 1: Get the tag_text of tags associated with political parties
        political_party_tag_texts_query = """
            SELECT DISTINCT t.tag_text
            FROM tag_political_parties tp
            JOIN tags t ON tp.tag_id = t.id
        """

        cur.execute(political_party_tag_texts_query)
        political_party_tag_texts = [row[0] for row in cur.fetchall()]

        if not political_party_tag_texts:
            return jsonify({'top_political_parties': []})

        # Step 2: Find all tags that have the same tag_text as those associated with political parties
        tags_query = """
            SELECT id
            FROM tags
            WHERE tag_text = ANY(%s)
        """

        cur.execute(tags_query, (political_party_tag_texts,))
        tag_ids = [row[0] for row in cur.fetchall()]

        if not tag_ids:
            return jsonify({'top_political_parties': []})

        # Step 3: Retrieve articles associated with these tags and calculate statistics
        query = """
            WITH unique_party_articles AS (
                SELECT
                    a.id AS article_id,
                    pp.id AS party_id,
                    pp.image_url,
                    a.emotion
                FROM articles a
                JOIN tags t ON a.id = t.article_id
                JOIN (
                    SELECT DISTINCT tp.political_party_id, t.tag_text
                    FROM tag_political_parties tp
                    JOIN tags t ON tp.tag_id = t.id
                ) tp ON t.tag_text = tp.tag_text
                JOIN political_parties pp ON tp.political_party_id = pp.id
                WHERE a.published_date BETWEEN %s AND %s
                  AND t.id = ANY(%s)
                GROUP BY a.id, pp.id, pp.image_url, a.emotion
            )

            SELECT
                pp.id AS party_id,
                pp.abbreviation,
                pp.image_url,
                COUNT(DISTINCT upa.article_id) AS total_articles,
                SUM(CASE WHEN upa.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                SUM(CASE WHEN upa.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                SUM(CASE WHEN upa.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
            FROM unique_party_articles upa
            JOIN political_parties pp ON upa.party_id = pp.id
            GROUP BY pp.id, pp.abbreviation, pp.image_url
            ORDER BY total_articles DESC
            LIMIT 3
        """

        cur.execute(query, (start_date, end_date, tag_ids))
        rows = cur.fetchall()

        # Prepare response data
        top_political_parties = []
        for row in rows:
            party_id, abbreviation, image_url, total_articles, positive_articles, negative_articles, neutral_articles = row
            top_political_parties.append({
                'party_id': party_id,
                'abbreviation': abbreviation,
                'image_url': image_url,
                'total_articles': total_articles,
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'neutral_articles': neutral_articles
            })

        return jsonify({'top_political_parties': top_political_parties})

    except psycopg2.Error as e:
        print("Error fetching top political parties:", e)
        return jsonify({"error": "Failed to fetch top political parties"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500
    
@statistics_bp.route('/api/top-cities', methods=['GET'])
def get_top_cities():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Use current date if start_date or end_date is not provided
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, microseconds=-1)

        cur = g.db_cursor

        # Step 1: Get the tag_text of tags associated with political parties
        city_tag_texts_query = """
            SELECT DISTINCT t.tag_text
            FROM tag_city tp
            JOIN tags t ON tp.tag_id = t.id
        """

        cur.execute(city_tag_texts_query)
        city_tag_texts = [row[0] for row in cur.fetchall()]

        if not city_tag_texts:
            return jsonify({'top_cities': []})

        # Step 2: Find all tags that have the same tag_text as those associated with political parties
        tags_query = """
            SELECT id
            FROM tags
            WHERE tag_text = ANY(%s)
        """

        cur.execute(tags_query, (city_tag_texts,))
        tag_ids = [row[0] for row in cur.fetchall()]

        if not tag_ids:
            return jsonify({'top_cities': []})

        # Step 3: Retrieve articles associated with these tags and calculate statistics
        query = """
            WITH unique_city_articles AS (
                SELECT
                    a.id AS article_id,
                    pp.id AS city_id,
                    pp.image_url,
                    a.emotion
                FROM articles a
                JOIN tags t ON a.id = t.article_id
                JOIN (
                    SELECT DISTINCT tp.city_id, t.tag_text
                    FROM tag_city tp
                    JOIN tags t ON tp.tag_id = t.id
                ) tp ON t.tag_text = tp.tag_text
                JOIN cities pp ON tp.city_id = pp.id
                WHERE a.published_date BETWEEN %s AND %s
                  AND t.id = ANY(%s)
                GROUP BY a.id, pp.id, pp.image_url, a.emotion
            )

            SELECT
                pp.id AS city_id,
                pp.name,
                pp.image_url,
                COUNT(DISTINCT upa.article_id) AS total_articles,
                SUM(CASE WHEN upa.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                SUM(CASE WHEN upa.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                SUM(CASE WHEN upa.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
            FROM unique_city_articles upa
            JOIN cities pp ON upa.city_id = pp.id
            GROUP BY pp.id, pp.name, pp.image_url
            ORDER BY total_articles DESC
            LIMIT 3
        """

        cur.execute(query, (start_date, end_date, tag_ids))
        rows = cur.fetchall()

        # Prepare response data
        top_cities = []
        for row in rows:
            party_id, name, image_url, total_articles, positive_articles, negative_articles, neutral_articles = row
            top_cities.append({
                'city_id': party_id,
                'name': name,
                'image_url': image_url,
                'total_articles': total_articles,
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'neutral_articles': neutral_articles
            })

        return jsonify({'top_cities': top_cities})

    except psycopg2.Error as e:
        print("Error fetching top cities:", e)
        return jsonify({"error": "Failed to fetch top cities"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500

@statistics_bp.route('/api/top-sources', methods=['GET'])
def get_top_sources():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Use today's date if start_date or end_date is not provided
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, microseconds=-1)

        cur = g.db_cursor

        query = """
            SELECT 
                s.id AS source_id,
                s.name,
                s.image_url,
                COUNT(a.id) AS total_articles,
                SUM(CASE WHEN a.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
                SUM(CASE WHEN a.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
                SUM(CASE WHEN a.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
            FROM articles a
            JOIN sources s ON a.source = s.id
            WHERE a.published_date BETWEEN %s AND %s
            GROUP BY s.id, s.name, s.image_url
            ORDER BY total_articles DESC
            LIMIT 3
        """

        cur.execute(query, (start_date, end_date))
        rows = cur.fetchall()

        top_sources = []
        for row in rows:
            source_id, name, image_url, total_articles, positive_articles, negative_articles, neutral_articles = row
            top_sources.append({
                'source_id': source_id,
                'name': name,
                'image_url': image_url,
                'total_articles': total_articles,
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'neutral_articles': neutral_articles
            })

        return jsonify({'top_sources': top_sources})

    except psycopg2.Error as e:
        print("Error fetching top sources:", e)
        return jsonify({"error": "Failed to fetch top sources"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500

@statistics_bp.route('/api/election-articles-distribution', methods=['GET'])
def get_election_articles_distribution():
    try:
        end_date = datetime.now()
        start_date_param = request.args.get('start_date')
        
        if start_date_param:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=7)

        cur = g.db_cursor

        # Step 1: Get all the election categories excluding "Toate Alegerile"
        cur.execute("SELECT id, name FROM elections WHERE name != 'Toate Alegerile'")
        elections = cur.fetchall()

        # Prepare the result dictionary
        election_distribution = {election[1]: {} for election in elections}

        # Step 2: Get the tags associated with each election and count articles by date
        for election in elections:
            election_id, election_name = election

            # Fetch the tags associated with this election ID
            cur.execute("SELECT tag_text FROM tags WHERE id IN (SELECT tag_id FROM tag_election WHERE election_id = %s)", (election_id,))
            tags = [tag[0] for tag in cur.fetchall()]

            if not tags:
                continue

            # Fetch the article count per day for these tags
            cur.execute("""
                SELECT a.published_date::date AS article_date, COUNT(DISTINCT a.id) AS total_articles
                FROM articles AS a
                JOIN tags AS t ON a.id = t.article_id
                WHERE t.tag_text = ANY(%s)
                  AND a.published_date BETWEEN %s AND %s
                GROUP BY article_date
                ORDER BY article_date
            """, (tags, start_date, end_date))
            
            rows = cur.fetchall()

            for row in rows:
                article_date, total_articles = row
                election_distribution[election_name][article_date.strftime('%Y-%m-%d')] = total_articles

        return jsonify({'election_distribution': election_distribution})

    except Exception as e:
        print("Error fetching election articles distribution:", e)
        return jsonify({"error": "Failed to fetch election articles distribution"}), 500

@statistics_bp.route('/api/articles/last_30_days', methods=['GET'])
def get_articles_last_30_days():
    try:
        cur = g.db_cursor
        today_date = datetime.now().date()
        past_date = today_date - timedelta(days=30)

        cur.execute("""
            SELECT 
                DATE(a.published_date) AS date,
                COUNT(*) AS total_articles
            FROM articles AS a
            WHERE DATE(a.published_date) BETWEEN %s AND %s
            GROUP BY DATE(a.published_date)
            ORDER BY DATE(a.published_date)
        """, (past_date, today_date))
        
        results = cur.fetchall()
        articles_summary = [
            {
                'date': result[0].strftime('%Y-%m-%d'),
                'total_articles': result[1]
            }
            for result in results
        ]

        return jsonify(articles_summary)
    except Exception as e:
        print("Error fetching articles summary for the last 30 days:", e)
        return jsonify({"error": "Failed to fetch articles summary for the last 30 days"}), 500

@statistics_bp.route('/api/article-length-distribution', methods=['GET'])
def get_article_length_distribution():
    try:
        # Parse start_date and end_date from query parameters
        start_date_param = request.args.get('start_date')
        end_date_param = request.args.get('end_date')

        # Calculate start_date and end_date based on parameters or default to last 7 days
        if start_date_param and end_date_param:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d')
        else:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)

        cur = g.db_cursor
        # Fetch articles and their paragraphs within the specified date range
        cur.execute("""
            SELECT a.id, a.title, string_agg(ap.paragraph_text, ' ') AS article_text, a.emotion
            FROM articles a
            JOIN article_paragraphs ap ON a.id = ap.article_id
            WHERE a.published_date BETWEEN %s AND %s
            GROUP BY a.id, a.title, a.emotion
            ORDER BY a.id
        """, (start_date, end_date))

        articles = cur.fetchall()

        # Initialize a defaultdict to store article length distribution
        article_length_distribution = {
            'scurte': {'count': 0, 'negative': 0, 'positive': 0, 'neutral': 0},
            'medii': {'count': 0, 'negative': 0, 'positive': 0, 'neutral': 0},
            'lungi': {'count': 0, 'negative': 0, 'positive': 0, 'neutral': 0}
        }

        # Process data to calculate article lengths and aggregate sentiment
        for article_id, title, article_text, emotion in articles:
            # Remove HTML tags and non-alphanumeric characters
            clean_text = re.sub(r'<[^>]+>', '', article_text)
            clean_text = re.sub(r'\W+', ' ', clean_text)
            
            # Count words in article_text to determine article length
            word_count = len(clean_text.split())

            # Categorize article length
            if word_count < 300:
                length_category = 'scurte'
            elif word_count < 600:
                length_category = 'medii'
            else:
                length_category = 'lungi'

            # Categorize emotion
            if emotion == 'Negative':
                article_length_distribution[length_category]['negative'] += 1
            elif emotion == 'Positive':
                article_length_distribution[length_category]['positive'] += 1
            elif emotion == 'Neutral':
                article_length_distribution[length_category]['neutral'] += 1

            # Increment article count for the length category
            article_length_distribution[length_category]['count'] += 1

        # Prepare response data with aggregated sentiment
        response_data = {
            'article_length_distribution': article_length_distribution
        }

        return jsonify(response_data)

    except Exception as e:
        print("Error fetching article length distribution:", e)
        return jsonify({"error": "Failed to fetch article length distribution"}), 500

@statistics_bp.route('/api/top-authors', methods=['GET'])
def get_top_authors():
    try:
        # Parse start_date and end_date from query parameters
        start_date_param = request.args.get('start_date')
        end_date_param = request.args.get('end_date')

        # Calculate start_date and end_date based on parameters or default to today
        if start_date_param and end_date_param:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d')
        else:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=1)  # Adjusted for today

        # Get database cursor
        cur = g.db_cursor

        # Construct SQL query to fetch top three authors with most articles for today
        query = """
            SELECT
                ar.author AS author_name,
                COUNT(*) AS articles_count,
                SUM(CASE WHEN ar.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_count,
                SUM(CASE WHEN ar.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_count,
                SUM(CASE WHEN ar.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_count,
                s.id,
                s.name AS source_name,
                s.image_url AS source_image_url
            FROM
                articles ar
            JOIN
                sources s ON ar.source = s.id
            WHERE
                ar.published_date BETWEEN %s AND %s
            GROUP BY
                ar.author, s.id, s.name, s.image_url
            ORDER BY
                articles_count DESC
            LIMIT
                3
        """

        # Execute the query with start_date and end_date as parameters
        cur.execute(query, (start_date, end_date))
        top_authors = cur.fetchall()


        # Format the response data
        response_data = []
        for row in top_authors:
            author_name = row[0]
            articles_count = row[1]
            positive_count = row[2]
            negative_count = row[3]
            neutral_count = row[4]
            source_id = row[5]
            source_name = row[6]
            source_image_url = row[7]

            response_data.append({
                'author': author_name,
                'articles_count': articles_count,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'source': {
                    'id': source_id,
                    'name': source_name,
                    'image_url': source_image_url
                }
            })

        return jsonify(response_data)

    except Exception as e:
        print("Error fetching top authors:", e)
        return jsonify({"error": "Failed to fetch top authors"}), 500

@statistics_bp.route('/api/sentiment-over-time', methods=['GET'])
def get_sentiment_over_time():
    try:
        today = datetime.now().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        
        cur = g.db_cursor

        query = """
        SELECT published_date, emotion
        FROM articles
        WHERE published_date BETWEEN %s AND %s
        ORDER BY published_date;
        """

        cur.execute(query, (start_date, end_date))
        results = cur.fetchall()

        sentiment_data = [{'published_date': row[0], 'emotion': row[1]} for row in results]

        return jsonify(sentiment_data)

    except Exception as e:
        print("Error fetching sentiment over time:", e)
        return jsonify({"error": "Failed to fetch sentiment over time"}), 500

@statistics_bp.route('/api/related-entities/<int:article_id>', methods=['GET'])
def get_related_entities(article_id):
    try:
        cur = g.db_cursor

        query = """
        WITH article_tags AS (
            SELECT t.id, t.tag_text
            FROM tags t
            WHERE t.article_id = %s
        ),
        related_politicians AS (
            SELECT DISTINCT
                at.id AS tag_id,
                at.tag_text,
                tp.politician_id,
                CONCAT(p.first_name, ' ', p.last_name) AS politician_name,
                p.image_url
            FROM article_tags at
            JOIN tag_politician tp ON at.tag_text = (
                SELECT t2.tag_text
                FROM tags t2
                WHERE t2.id = tp.tag_id
            )
            JOIN politicians p ON tp.politician_id = p.id
        ),
        related_political_parties AS (
            SELECT DISTINCT
                at.id AS tag_id,
                at.tag_text,
                tp.political_party_id,
                pp.abbreviation,
                pp.image_url
            FROM article_tags at
            JOIN tag_political_parties tp ON at.tag_text = (
                SELECT t2.tag_text
                FROM tags t2
                WHERE t2.id = tp.tag_id
            )
            JOIN political_parties pp ON tp.political_party_id = pp.id
        ),
        related_cities AS (
            SELECT DISTINCT
                at.id AS tag_id,
                at.tag_text,
                tc.city_id,
                c.name,
                c.image_url
            FROM article_tags at
            JOIN tag_city tc ON at.tag_text = (
                SELECT t2.tag_text
                FROM tags t2
                WHERE t2.id = tc.tag_id
            )
            JOIN cities c ON tc.city_id = c.id
        )
        SELECT 
            'politician' AS entity_type,
            politician_id AS entity_id,
            politician_name AS entity_name,
            image_url
        FROM related_politicians
        UNION
        SELECT 
            'political-party' AS entity_type,
            political_party_id AS entity_id,
            abbreviation AS entity_name,
            image_url
        FROM related_political_parties
        UNION
        SELECT 
            'city' AS entity_type,
            city_id AS entity_id,
            name AS entity_name,
            image_url
        FROM related_cities;
        """

        cur.execute(query, (article_id,))
        rows = cur.fetchall()

        seen_entities = set()
        related_entities = []
        for row in rows:
            entity_type, entity_id, entity_name, image_url = row
            entity_key = (entity_type, entity_id)
            if entity_key not in seen_entities:
                seen_entities.add(entity_key)
                related_entities.append({
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'entity_name': entity_name,
                    'image_url': image_url
                })

        return jsonify({'related_entities': related_entities})

    except psycopg2.Error as e:
        print("Error fetching related entities:", e)
        return jsonify({"error": "Failed to fetch related entities"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500

@statistics_bp.route('/api/related-entities', methods=['GET'])
def get_related_entities_for_date_range():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Use current date if start_date or end_date is not provided
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, microseconds=-1)

        cur = g.db_cursor

        # Step 1: Retrieve all articles within the date range
        articles_query = """
            SELECT id, title, published_date, emotion
            FROM articles
            WHERE published_date BETWEEN %s AND %s
        """
        cur.execute(articles_query, (start_date, end_date))
        articles = cur.fetchall()

        if not articles:
            return jsonify({'related_entities': []})

        # Step 2: Prepare the list of article IDs
        article_ids = [article[0] for article in articles]

        # Step 3: Retrieve all tags for these articles
        tags_query = """
            SELECT t.article_id, t.id, t.tag_text
            FROM tags t
            WHERE t.article_id = ANY(%s)
        """
        cur.execute(tags_query, (article_ids,))
        tags = cur.fetchall()

        if not tags:
            return jsonify({'related_entities': []})

        # Step 4: Check if these tags are associated with politicians, political parties, or cities
        related_entities_query = """
            WITH article_tags AS (
                SELECT t.article_id, t.id, t.tag_text
                FROM tags t
                WHERE t.article_id = ANY(%s)
            )
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
        """
        cur.execute(related_entities_query, (article_ids,))
        related_entities = cur.fetchall()

        # Organize related entities by entity_id
        entities_count = {}
        for entity in related_entities:
            article_id, entity_type, entity_id, entity_name, image_url = entity

            # Initialize entity in the dictionary if not already present
            if entity_id not in entities_count:
                entities_count[entity_id] = {
                    'entity_type': entity_type,
                    'entity_id': entity_id,  # Include entity_id in the response
                    'entity_name': entity_name,
                    'image_url': image_url,
                    'total_articles': 0,
                    'positive_articles': 0,
                    'negative_articles': 0,
                    'neutral_articles': 0
                }

            # Update counts based on sentiment
            for article in articles:
                if article[0] == article_id:
                    entities_count[entity_id]['total_articles'] += 1
                    if article[3] == 'Positive':
                        entities_count[entity_id]['positive_articles'] += 1
                    elif article[3] == 'Negative':
                        entities_count[entity_id]['negative_articles'] += 1
                    else:
                        entities_count[entity_id]['neutral_articles'] += 1

        # Filter entities with at least 15 articles and calculate percentages
        filtered_entities = []
        for entity_id, counts in entities_count.items():
            if counts['total_articles'] >= 15:
                positive_percentage = (counts['positive_articles'] / counts['total_articles']) * 100
                negative_percentage = (counts['negative_articles'] / counts['total_articles']) * 100
                neutral_percentage = (counts['neutral_articles'] / counts['total_articles']) * 100
                counts['positive_percentage'] = positive_percentage
                counts['negative_percentage'] = negative_percentage
                counts['neutral_percentage'] = neutral_percentage
                filtered_entities.append(counts)

        # Sort to find the most positive, most negative, and most neutral entities
        most_positive = max(filtered_entities, key=lambda x: x['positive_percentage'], default=None)
        most_negative = max(filtered_entities, key=lambda x: x['negative_percentage'], default=None)
        most_neutral = max(filtered_entities, key=lambda x: x['neutral_percentage'], default=None)

        # Prepare the final response with only the three selected entities
        response = {
            'most_positive': most_positive,
            'most_negative': most_negative,
            'most_neutral': most_neutral
        }

        return jsonify(response)

    except psycopg2.Error as e:
        print("Error fetching related entities for date range:", e)
        return jsonify({"error": "Failed to fetch related entities for date range"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500

@statistics_bp.route('/api/top-entity-pairs', methods=['GET'])
def get_top_entity_pairs():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(microseconds=1)

        cur = g.db_cursor

        # SQL query to fetch top pairs of entities
        query = """
            WITH articles_period AS (
                SELECT id AS article_id, title, published_date
                FROM articles
                WHERE published_date::date BETWEEN %s AND %s
            ),

            article_tags AS (
                SELECT t.article_id, t.id AS tag_id, t.tag_text
                FROM tags t
                JOIN articles_period a ON t.article_id = a.article_id
            ),

            related_entities AS (
                -- Politicians
                SELECT
                    at.article_id,
                    'politician' AS entity_type,
                    tp.politician_id AS entity_id,
                    CONCAT(p.first_name, ' ', p.last_name) AS entity_name,
                    p.image_url,
                    a.emotion
                FROM article_tags at
                JOIN tag_politician tp ON at.tag_text = (
                    SELECT t2.tag_text
                    FROM tags t2
                    WHERE t2.id = tp.tag_id
                )
                JOIN politicians p ON tp.politician_id = p.id
                JOIN articles a ON at.article_id = a.id

                UNION ALL

                -- Political Parties
                SELECT
                    at.article_id,
                    'political-party' AS entity_type,
                    tp.political_party_id AS entity_id,
                    pp.abbreviation AS entity_name,
                    pp.image_url,
                    a.emotion
                FROM article_tags at
                JOIN tag_political_parties tp ON at.tag_text = (
                    SELECT t2.tag_text
                    FROM tags t2
                    WHERE t2.id = tp.tag_id
                )
                JOIN political_parties pp ON tp.political_party_id = pp.id
                JOIN articles a ON at.article_id = a.id

                UNION ALL

                -- Cities
                SELECT
                    at.article_id,
                    'city' AS entity_type,
                    tc.city_id AS entity_id,
                    c.name AS entity_name,
                    c.image_url,
                    a.emotion
                FROM article_tags at
                JOIN tag_city tc ON at.tag_text = (
                    SELECT t2.tag_text
                    FROM tags t2
                    WHERE t2.id = tc.tag_id
                )
                JOIN cities c ON tc.city_id = c.id
                JOIN articles a ON at.article_id = a.id
            ),

            same_entity_pairs AS (
                SELECT
                    re1.entity_type AS entity_type1,
                    re1.entity_id AS entity_id1,
                    re1.entity_name AS entity_name1,
                    re1.image_url AS entity1_image_url,
                    re2.entity_id AS entity_id2,
                    re2.entity_name AS entity_name2,
                    re2.image_url AS entity2_image_url,
                    COUNT(*) AS pair_count,
                    SUM(CASE WHEN re1.emotion = 'Positive' THEN 1 ELSE 0 END) AS positive_count,
                    SUM(CASE WHEN re1.emotion = 'Negative' THEN 1 ELSE 0 END) AS negative_count,
                    SUM(CASE WHEN re1.emotion = 'Neutral' THEN 1 ELSE 0 END) AS neutral_count
                FROM related_entities re1
                JOIN related_entities re2 ON re1.article_id = re2.article_id
                                           AND re1.entity_type = re2.entity_type
                                           AND re1.entity_id < re2.entity_id
                GROUP BY re1.entity_type, re1.entity_id, re1.entity_name, re1.image_url,
                         re2.entity_id, re2.entity_name, re2.image_url
            ),

            ranked_pairs AS (
                SELECT
                    entity_type1,
                    entity_id1,
                    entity_name1,
                    entity1_image_url,
                    entity_id2,
                    entity_name2,
                    entity2_image_url,
                    pair_count,
                    positive_count,
                    negative_count,
                    neutral_count,
                    ROW_NUMBER() OVER (ORDER BY pair_count DESC) AS pair_rank
                FROM same_entity_pairs
            )

            SELECT
                entity_type1,
                entity_id1,
                entity_name1,
                entity1_image_url,
                entity_id2,
                entity_name2,
                entity2_image_url,
                pair_count,
                positive_count,
                negative_count,
                neutral_count
            FROM ranked_pairs
            WHERE pair_rank <= 3
            ORDER BY pair_rank;
        """

        # Execute the query with parameters
        cur.execute(query, (start_date, end_date))
        rows = cur.fetchall()

        # Prepare response data
        top_entity_pairs = []
        for row in rows:
            entity_type1, entity_id1, entity_name1, entity1_image_url, entity_id2, entity_name2, entity2_image_url, pair_count, positive_count, negative_count, neutral_count = row
            top_entity_pairs.append({
                'entity_type1': entity_type1,
                'entity_id1': entity_id1,
                'entity_name1': entity_name1,
                'entity1_image_url': entity1_image_url,
                'entity_id2': entity_id2,
                'entity_name2': entity_name2,
                'entity2_image_url': entity2_image_url,
                'pair_count': pair_count,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count
            })

        return jsonify({'top_entity_pairs': top_entity_pairs})

    except psycopg2.Error as e:
        print("Error fetching top entity pairs:", e)
        return jsonify({"error": "Failed to fetch top entity pairs"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500




### ENTITIES PAGE ###

@statistics_bp.route('/api/articles/emotion-distribution', methods=['GET'])
def get_emotion_distribution():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = """
            SELECT s.id, s.name, s.image_url, a.emotion, COUNT(*)
            FROM articles AS a
            JOIN sources AS s ON a.source = s.id
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND DATE(a.published_date) >= %s"
            params.append(start_date)

        if end_date:
            query += " AND DATE(a.published_date) <= %s"
            params.append(end_date)

        query += " GROUP BY s.id, s.name, s.image_url, a.emotion"

        cur = g.db_cursor
        cur.execute(query, tuple(params))
        results = cur.fetchall()

        emotion_distribution = {}
        for source_id, name, image_url, emotion, count in results:
            if name not in emotion_distribution:
                emotion_distribution[name] = {
                    'id': source_id,
                    'image_url': image_url,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0
                }
            emotion_distribution[name][emotion.lower()] = count

        return jsonify(emotion_distribution)
    except Exception as e:
        print("Error fetching emotion distribution:", e)
        return jsonify({"error": "Failed to fetch emotion distribution"}), 500


### ARTICLE DETAILS ###

@statistics_bp.route('/api/entity-articles', methods=['GET'])
def get_entity_articles_by_date_range():
    try:
        entity_id = request.args.get('entityId')
        entity_type = request.args.get('entityType')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Validate required parameters
        if not entity_id or not entity_type:
            return jsonify({"error": "Missing required parameters: entityId and entityType"}), 400

        # Set default dates if not provided
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, microseconds=-1)

        # Calculate the date range for the last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)

        cur = g.db_cursor

        # Step 1: Fetch tags for the specified entity
        if entity_type == 'politician':
            tags_query = """
                SELECT t.tag_text
                FROM tags t
                JOIN tag_politician tp ON t.id = tp.tag_id
                WHERE tp.politician_id = %s
            """
        elif entity_type == 'political-party':
            tags_query = """
                SELECT t.tag_text
                FROM tags t
                JOIN tag_political_parties tp ON t.id = tp.tag_id
                WHERE tp.political_party_id = %s
            """
        elif entity_type == 'city':
            tags_query = """
                SELECT t.tag_text
                FROM tags t
                JOIN tag_city tc ON t.id = tc.tag_id
                WHERE tc.city_id = %s
            """
        else:
            return jsonify({"error": "Invalid entityType"}), 400

        cur.execute(tags_query, (entity_id,))
        tags = cur.fetchall()

        if not tags:
            return jsonify({'counts': {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}})

        # Extract tag texts
        tag_texts = [tag[0] for tag in tags]

        # Step 2: Retrieve all articles within the last 7 days that have these tags
        articles_query = """
            SELECT a.id, a.title, a.published_date, a.emotion
            FROM articles a
            JOIN tags t ON a.id = t.article_id
            WHERE t.tag_text = ANY(%s) AND a.published_date BETWEEN %s AND %s
        """
        cur.execute(articles_query, (tag_texts, seven_days_ago, end_date))
        articles = cur.fetchall()

        if not articles:
            return jsonify({'counts': {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}})

        # Step 3: Count articles by their type
        counts = {
            'total': len(articles),
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }

        for article in articles:
            emotion = article[3]
            if emotion == 'Positive':
                counts['positive'] += 1
            elif emotion == 'Negative':
                counts['negative'] += 1
            else:
                counts['neutral'] += 1

        return jsonify({
            'entity_id': entity_id,
            'entity_type': entity_type,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'counts': counts
        })

    except psycopg2.Error as e:
        print("Error fetching entity articles:", e)
        return jsonify({"error": "Failed to fetch entity articles"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500
 
@statistics_bp.route('/api/article-analytics/<int:article_id>', methods=['GET'])
def get_article_analytics(article_id):
    try:
        # Fetch the current article details
        cur = g.db_cursor

        cur.execute("""
            SELECT a.title
            FROM articles a
            WHERE a.id = %s
        """, (article_id,))
        current_article = cur.fetchone()
        if not current_article:
            return jsonify({"error": "Article not found"}), 404

        current_article_title = current_article[0]

        # Get the start and end dates from request parameters or default to the last 7 days
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        if not start_date or not end_date:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Fetch all articles in the specified date range
        cur.execute("""
            SELECT a.id, a.title, a.emotion
            FROM articles a
            WHERE a.published_date BETWEEN %s AND %s
        """, (start_date, end_date))
        articles = cur.fetchall()

        # Ensure articles list is not empty
        if not articles:
            return jsonify({"error": "No articles found in the specified date range"}), 404

        # Preprocess article titles for Romanian
        def preprocess_text_ro(text):
            # Normalize text, remove non-alphanumeric characters, and lowercase
            text = re.sub(r'[^\w\s]', '', text)
            text = text.lower()
            # Tokenize, lemmatize, and remove stopwords
            doc = nlp(text)
            tokens = [token.lemma_ for token in doc if not token.is_stop]
            return ' '.join(tokens)

        # Preprocess current article title
        current_article_title = preprocess_text_ro(current_article_title)

        # Preprocess all other article titles
        article_titles = [preprocess_text_ro(article[1]) for article in articles]

        # Vectorize article titles
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform([current_article_title] + article_titles)


        # Calculate cosine similarity
        similarities = cosine_similarity(X[0], X[1:]).flatten()

        # Adjust similarity threshold
        similarity_threshold = 0.15  # Adjust the threshold value as needed
        similar_articles = [articles[idx] for idx in range(len(similarities)) if similarities[idx] > similarity_threshold]

        # Count emotions for similar articles
        emotion_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        for article in similar_articles:
            emotion = article[2]
            if emotion in emotion_counts:
                emotion_counts[emotion] += 1

        return jsonify({
            "similar_articles_count": len(similar_articles),
            "emotion_counts": emotion_counts
        })

    except Exception as e:
        print("Error fetching article analytics:", e)
        return jsonify({"error": "Failed to fetch article analytics"}), 500

@statistics_bp.route('/api/entity-pair-analytics', methods=['GET'])
def get_entity_pair_analytics():
    try:
        # Extract parameters from the request
        entity1_id = request.args.get('entity1Id')
        entity1_type = request.args.get('entity1Type')
        entity2_id = request.args.get('entity2Id')
        entity2_type = request.args.get('entity2Type')

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Validate required parameters
        if not entity1_id or not entity1_type or not entity2_id or not entity2_type:
            return jsonify({"error": "Missing required parameters: entity1Id, entity1Type, entity2Id, entity2Type"}), 400

        # Set default dates if not provided
        if not start_date:
            # Calculate 7 days ago
            seven_days_ago = datetime.now() - timedelta(days=7)
            start_date = seven_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, microseconds=-1)

        # Get the database cursor from the global context (assuming it's set up elsewhere)
        cur = g.db_cursor

        # Step 1: Fetch tags for entity 1
        entity1_tags_query = get_tags_query(entity1_type, entity1_id)
        cur.execute(entity1_tags_query, (entity1_id,))
        entity1_tags = cur.fetchall()

        if not entity1_tags:
            return jsonify({'counts': {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}})

        entity1_tag_texts = [tag[0] for tag in entity1_tags]

        # Step 2: Fetch tags for entity 2
        entity2_tags_query = get_tags_query(entity2_type, entity2_id)
        cur.execute(entity2_tags_query, (entity2_id,))
        entity2_tags = cur.fetchall()

        if not entity2_tags:
            return jsonify({'counts': {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}})

        entity2_tag_texts = [tag[0] for tag in entity2_tags]

        # Step 3: Retrieve articles containing both entity 1 and entity 2 within the specified date range
        articles_query = """
            SELECT a.id, a.title, a.published_date, a.emotion
            FROM articles a
            JOIN tags t1 ON a.id = t1.article_id
            JOIN tags t2 ON a.id = t2.article_id
            WHERE t1.tag_text = ANY(%s) AND t2.tag_text = ANY(%s)
              AND a.published_date BETWEEN %s AND %s
        """
        cur.execute(articles_query, (entity1_tag_texts, entity2_tag_texts, start_date, end_date))
        articles = cur.fetchall()

        if not articles:
            return jsonify({'counts': {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}})

        # Step 4: Count articles by their emotion
        counts = {
            'total': len(articles),
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }

        for article in articles:
            emotion = article[3]
            if emotion == 'Positive':
                counts['positive'] += 1
            elif emotion == 'Negative':
                counts['negative'] += 1
            else:
                counts['neutral'] += 1

        # Return JSON response
        return jsonify({
            'entity1_id': entity1_id,
            'entity1_type': entity1_type,
            'entity2_id': entity2_id,
            'entity2_type': entity2_type,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'counts': counts
        })

    except psycopg2.Error as e:
        print("Error fetching entity pair analytics:", e)
        return jsonify({"error": "Failed to fetch entity pair analytics"}), 500
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Unexpected error occurred"}), 500

def get_tags_query(entity_type, entity_id):
    # Define queries based on entity type
    if entity_type == 'politician':
        return """
            SELECT t.tag_text
            FROM tags t
            JOIN tag_politician tp ON t.id = tp.tag_id
            WHERE tp.politician_id = %s
        """
    elif entity_type == 'political-party':
        return """
            SELECT t.tag_text
            FROM tags t
            JOIN tag_political_parties tp ON t.id = tp.tag_id
            WHERE tp.political_party_id = %s
        """
    elif entity_type == 'city':
        return """
            SELECT t.tag_text
            FROM tags t
            JOIN tag_city tc ON t.id = tc.tag_id
            WHERE tc.city_id = %s
        """
    else:
        raise ValueError("Invalid entityType")


