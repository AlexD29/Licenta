from sqlalchemy.sql import func
import unicodedata
from .models import Article, Politician, PoliticalParty, City, Tag, TagCity, TagPoliticalParty, TagPolitician

def normalize_string(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def query_articles(query):
    normalized_query = normalize_string(query).lower()
    articles = Article.query.filter(func.unaccent(func.lower(Article.title)).ilike(f'%{normalized_query}%')).all()

    article_suggestions = []
    for article in articles:
        article_dict = {
            "title": article.title,
            "url": article.url,
            "author": article.author,
            "published_date": article.published_date,
            "number_of_views": article.number_of_views,
            "image_url": article.image_url,
            "source": article.source,
            "emotion": article.emotion,
            "category": "Article"
        }
        article_suggestions.append(article_dict)
    return article_suggestions

def query_politicians(query):
    normalized_query = normalize_string(query).lower()
    politicians = Politician.query.filter(
        (func.unaccent(func.lower(Politician.first_name)).ilike(f'%{normalized_query}%')) |
        (func.unaccent(func.lower(Politician.last_name)).ilike(f'%{normalized_query}%')) |
        (func.unaccent(func.lower(Politician.city)).ilike(f'%{normalized_query}%'))
    ).all()

    politician_suggestions = []
    for politician in politicians:
        politician_dict = {
            "id": politician.id,
            "first_name": politician.first_name,
            "last_name": politician.last_name,
            "image_url": politician.image_url,
            "category": "Politician"
        }
        politician_suggestions.append(politician_dict)
    return politician_suggestions

def query_political_parties(query):
    normalized_query = normalize_string(query).lower()  # Normalize and lowercase the query on the client-side
    political_parties = PoliticalParty.query.filter(
        (func.unaccent(func.lower(PoliticalParty.abbreviation)).ilike(f'%{normalized_query}%')) |
        (func.unaccent(func.lower(PoliticalParty.full_name)).ilike(f'%{normalized_query}%'))
    ).all()
    
    political_party_suggestions = []
    for political_party in political_parties:
        political_party_dict = {
            "id": political_party.id,
            "abbreviation": political_party.abbreviation,
            "image_url": political_party.image_url,
            "category": "Partid politic"
        }
        political_party_suggestions.append(political_party_dict)
    return political_party_suggestions

def query_cities(query):
    normalized_query = normalize_string(query).lower()
    cities = City.query.filter(
        (func.unaccent(func.lower(City.name)).ilike(f'%{normalized_query}%'))
    ).all()

    city_suggestions = []
    for city in cities:
        city_dict = {
            "id": city.id,
            "name": city.name,
            "image_url": city.image_url,
            "category": "Oraș"
        }
        city_suggestions.append(city_dict)
    return city_suggestions

def query_tags(query):
    normalized_query = normalize_string(query).lower()
    tags = Tag.query.filter(
        (func.unaccent(func.lower(Tag.tag_text)).ilike(f'%{normalized_query}%'))
    ).all()

    tags_suggestions = []
    for tag in tags:
        tag_dict = {
            "tag_text": tag.tag_text,
            "category": "Tag"
        }
        tags_suggestions.append(tag_dict)
    return tags_suggestions

def query_articles_by_tags(tags):
    articles = []
    for tag in tags:
        articles.extend(Article.query.filter_by(tag_id=tag.id).all())
    return articles

def query_tags_for_politician(politician_id):
    politician = Politician.query.get(politician_id)
    return politician.tags

def get_tags_for_entity(entity):
    if entity['category'] == 'Politician':
        return get_tags_for_politician(entity['id'])
    elif entity['category'] == 'Partid politic':
        return get_tags_for_political_party(entity['id'])
    elif entity['category'] == 'Oraș':
        return get_tags_for_city(entity['id'])
    else:
        return []

def get_tags_for_politician(politician_id):
    tags = Tag.query.join(TagPolitician).filter(TagPolitician.politician_id == politician_id).all()
    return [tag.tag_text for tag in tags]

def get_tags_for_political_party(party_id):
    tags = Tag.query.join(TagPoliticalParty).filter(TagPoliticalParty.party_id == party_id).all()
    return [tag.tag_text for tag in tags]

def get_tags_for_city(city_id):
    tags = Tag.query.join(TagCity).filter(TagCity.city_id == city_id).all()
    return [tag.tag_text for tag in tags]

