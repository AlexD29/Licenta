# stats_routes.py
from flask import Blueprint, jsonify, request, g
from datetime import datetime

statistics_bp = Blueprint('statistics', __name__)

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
