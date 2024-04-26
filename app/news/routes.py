from . import bp
from flask import jsonify

@bp.route('/api/get_news', methods=['GET'])
def get_news():
    # Your logic to fetch news data
    news_data = [{'title': 'News 1', 'content': 'Content 1'}, {'title': 'News 2', 'content': 'Content 2'}]
    return jsonify(news_data)

