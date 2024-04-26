from datetime import datetime, timezone, timedelta

import requests
from googletrans import Translator, constants
from pprint import pprint

from langid import langid


#
# translator = Translator()
#
# translation = translator.translate("bUNA ZIUA OAMENI")
# print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")


def extract_date(date_string):
    formats_to_try = [
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats_to_try:
        try:
            date_time_obj = datetime.strptime(date_string, fmt)
            date_time_obj = date_time_obj.replace(tzinfo=timezone.utc)
            return date_time_obj
        except ValueError:
            pass

    # If none of the formats match, raise an error
    raise ValueError(f"Could not parse date: {date_string}")


def format_date(input_date):
    try:
        date_time_obj = datetime.strptime(input_date, '%Y-%m-%d %H:%M:%S%z')
        formatted_date = date_time_obj.strftime('%d.%m.%Y %H:%M')
        return formatted_date

    except ValueError as e:
        print(f"Error formatting date: {e}")
        return None


def is_english(text):
    lang, _ = langid.classify(text)
    return lang == 'en'

def get_news():
    #topic = self.topic_var.get()

    #if not topic:
        #self.insert_card("Please enter a topic to search.")
        #return

    api_keys = {
        'newsapi': '3ef695980afe4eb685bf37daef1d574d',
        'guardian': 'bdb1c135-cf0b-45f0-b098-db003ccd3b74',
        'mediastack': '251b56cf780d3d220c9f5a4cef7c2f16',
        'newsdata': 'pub_360972b3a808f11528343f275ac3c7f3744b3',
        'worldnewsapi': 'afb4f3873ef9488abe807c17e94dc09d',
        'gnews': '0f69b52adff4d32d47f2b5ce1387d0d4',
    }

# //, 'guardian', , , 'worldnewsapi',
    sources = ['mediastack']

    all_news = []

    for source in sources:
        api_key = api_keys.get(source)
        if api_key:
            if source == 'newsapi':
                url = f'https://{source}.org/v2/top-headlines?country=ro&apiKey={api_key}'
            # elif source == 'guardian':
            #     url = f'https://content.guardianapis.com/search?q={topic}&api-key={api_key}'
            #nu stiu de ce nu merge mediastack
            # elif source == 'mediastack':
            #     url = f'http://api.mediastack.com/v1/news?access_key={api_key}&countries=ro&language=ro'
            elif source == 'newsdata':
                url = f'https://newsdata.io/api/1/news?country=ro&apikey={api_key}'
            # elif source == 'worldnewsapi':
            #     url = f'https://api.worldnewsapi.com/search-news?api-key={api_key}&text={topic}'
            elif source == 'gnews':
                url = f'https://gnews.io/api/v4/top-headlines?country=ro&category=general&apikey={api_key}'

            response = requests.get(url)

            if response.status_code == 200:
                news_data = response.json()

                if source == 'newsapi':
                    articles = news_data.get('articles', [])
                    for article in articles:
                        published_at = extract_date(article.get('publishedAt', ''))
                        if published_at >= datetime.now(timezone.utc) - timedelta(days=10):
                            author = article.get('author', '')
                            content = article.get('content', '')
                            title = article.get('title', '')
                            source_name = article.get('source', {}).get('name', '')
                            description = article.get('description', '')
                            url_to_image = article.get('urlToImage', '')
                            web_url = article.get('url', '')
                            all_news.append({
                                'source': "News API",
                                'author': author,
                                'content': content,
                                'title': title,
                                'extra_info': f"Source: {source_name}",
                                'description': description,
                                'image_url': url_to_image,
                                'published_at': published_at,
                                'web_url': web_url,
                            })

                elif source == 'guardian':
                    results = news_data.get('response', {}).get('results', [])
                    for article in results:
                        published_at = extract_date(article.get('webPublicationDate', ''))
                        if published_at >= datetime.now(timezone.utc) - timedelta(days=10):
                            title = article.get('webTitle', '')
                            web_url = article.get('webUrl', '')
                            author = article.get('fields', {}).get('byline', '').replace('By ', '')
                            thumbnail = article.get('fields', {}).get('thumbnail', '')
                            all_news.append({
                                'source': "The Guardian",
                                'author': author,
                                'content': '',
                                'title': title,
                                'extra_info': f"URL: {web_url}",
                                'description': '',
                                'image_url': thumbnail,
                                'published_at': published_at,
                                'web_url': web_url,
                            })

                elif source == 'mediastack':
                    data = news_data.get('data', [])
                    for article in data:
                        published_at = extract_date(article.get('published_at', ''))
                        if published_at >= datetime.now(timezone.utc) - timedelta(days=10):
                            title = article.get('title', '')
                            if is_english(title):
                                source_name = article.get('source', '')
                                description = article.get('description', '')
                                author = article.get('author', '')
                                image_url = article.get('image', '')
                                web_url = article.get('url', '')
                                all_news.append({
                                    'source': "Media Stack",
                                    'author': author,
                                    'content': description,
                                    'title': title,
                                    'extra_info': f"Source: {source_name}",
                                    'description': description,
                                    'image_url': image_url,
                                    'published_at': published_at,
                                    'web_url': web_url,
                                })

                elif source == 'newsdata':
                    articles = news_data.get('results', [])
                    for article in articles:
                        published_at = extract_date(article.get('pubDate', ''))
                        if published_at >= datetime.now(timezone.utc) - timedelta(days=10):
                            title = article.get('title', '')
                            source_name = article.get('source', '')
                            description = article.get('description', '')
                            content = article.get('content', '')

                            creator = article.get('creator', [])
                            if creator is not None and isinstance(creator, list):
                                creator = [c for c in creator if c is not None]

                            author = ', '.join(map(str, creator)) if creator else None
                            image_url = article.get('image', '')
                            web_url = article.get('url', '')

                            all_news.append({
                                'source': "Newsdata.io",
                                'author': author,
                                'content': content,
                                'title': title,
                                'extra_info': f"Source: {source_name}",
                                'description': description,
                                'image_url': image_url,
                                'published_at': published_at,
                                'web_url': web_url,
                            })

                elif source == 'worldnewsapi':
                    articles = news_data.get('news', [])
                    for article in articles:
                        published_at = extract_date(
                            article.get('publish_date', ''))
                        if published_at >= datetime.now(timezone.utc) - timedelta(days=10):
                            author = ', '.join(article.get('authors', []))
                            content = article.get('text', '')
                            title = article.get('title', '')
                            source_name = "World News API"
                            description = article.get('summary', '')
                            image_url = article.get('image', '')
                            web_url = article.get('url', '')
                            all_news.append({
                                'source': source_name,
                                'author': author,
                                'content': content,
                                'title': title,
                                'extra_info': f"Source: {source_name}",
                                'description': description,
                                'image_url': image_url,
                                'published_at': published_at,
                                'web_url': web_url,
                            })

                elif source == 'gnews':
                    articles = news_data.get('articles', [])
                    for article in articles:
                        published_at = extract_date(article.get('publishedAt', ''))
                        if published_at >= datetime.now(timezone.utc) - timedelta(days=10):
                            title = article.get('title', '')
                            source_name = article.get('source', '')
                            description = article.get('description', '')
                            content = article.get('content', '')
                            author = article.get('author', '')
                            image_url = article.get('image', '')
                            web_url = article.get('url', '')

                            all_news.append({
                                'source': "GNews API",
                                'author': author,
                                'content': content,
                                'title': title,
                                'extra_info': f"Source: {source_name}",
                                'description': description,
                                'image_url': image_url,
                                'published_at': published_at,
                                'web_url': web_url,
                            })

            else:
                all_news.append({
                    'source': f"We couldn't get the news from source {source}. Check the internet connection and try again."
                })

        else:
            all_news.append({
                'source': f"API key is missing for source {source}."
            })

    sorted_news = sorted(all_news, key=lambda x: x.get('published_at'), reverse=True)

    print(sorted_news)
    print(len(sorted_news))

get_news()