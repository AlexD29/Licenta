from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from app.routes import db
import unicodedata
from .models import Article, Politician, PoliticalParty, City, Tag, Election, Source, TagCity, TagPoliticalParty, TagPolitician

def normalize_string(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def query_articles(query):
    normalized_query = normalize_string(query).lower()
    query_parts = normalized_query.split()

    if not query_parts:
        return []

    filters = [
        func.unaccent(func.lower(Article.title)).ilike(f'%{part}%')
        for part in query_parts
    ]

    query_filter = and_(*filters)

    # Perform the join with the Source table
    articles = (
        db.session.query(Article, Source)
        .join(Source, Article.source == Source.id)
        .filter(query_filter)
        .order_by(desc(Article.published_date))
        .all()
    )

    prioritized_articles = []
    other_articles = []

    for article, source in articles:
        title = article.title.lower()
        if normalized_query in title:
            prioritized_articles.append((article, source))
        else:
            other_articles.append((article, source))

    sorted_articles = prioritized_articles + other_articles

    article_suggestions = []
    for article, source in sorted_articles:
        article_dict = {
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "author": article.author,
            "published_date": article.published_date,
            "number_of_views": article.number_of_views,
            "image_url": article.image_url,
            "source": {
                "name": source.name,
                "image_url": source.image_url
            },
            "emotion": article.emotion,
            "category": "Article"
        }
        article_suggestions.append(article_dict)

    return article_suggestions

def query_politicians(query):
    normalized_query = normalize_string(query).lower()
    query_parts = normalized_query.split()

    if not query_parts:
        return []

    # Build filters for each part of the query
    filters = [
        or_(
            func.unaccent(func.lower(Politician.first_name)).ilike(f'%{part}%'),
            func.unaccent(func.lower(Politician.last_name)).ilike(f'%{part}%'),
            func.unaccent(func.lower(Politician.city)).ilike(f'%{part}%')
        )
        for part in query_parts
    ]

    # Combine filters with AND to ensure all parts are matched
    query_filter = and_(*filters)
    politicians = Politician.query.filter(query_filter).all()

    # Additional filtering to prioritize exact sequence matches
    prioritized_politicians = []
    other_politicians = []

    for politician in politicians:
        full_name = f"{politician.first_name} {politician.last_name}".lower()
        if normalized_query in full_name:
            prioritized_politicians.append(politician)
        else:
            other_politicians.append(politician)

    # Combine prioritized and other politicians, ensuring all matches are returned
    sorted_politicians = prioritized_politicians + other_politicians

    politician_suggestions = []
    for politician in sorted_politicians:
        politician_dict = {
            "id": politician.id,
            "first_name": politician.first_name,
            "last_name": politician.last_name,
            "image_url": politician.image_url,
            "position": politician.position,
            "category": "Politician"
        }
        politician_suggestions.append(politician_dict)

    return politician_suggestions

def query_political_parties(query):
    normalized_query = normalize_string(query).lower()
    query_parts = normalized_query.split()

    if not query_parts:
        return []

    # Build filters for each part of the query
    filters = [
        or_(
            func.unaccent(func.lower(PoliticalParty.abbreviation)).ilike(f'%{part}%'),
            func.unaccent(func.lower(PoliticalParty.full_name)).ilike(f'%{part}%')
        )
        for part in query_parts
    ]

    # Combine filters with AND to ensure all parts are matched
    query_filter = and_(*filters)
    political_parties = PoliticalParty.query.filter(query_filter).all()

    # Additional filtering to prioritize exact sequence matches
    prioritized_political_parties = []
    other_political_parties = []

    for political_party in political_parties:
        full_name = political_party.full_name.lower()
        abbreviation = political_party.abbreviation.lower()
        if normalized_query in full_name or normalized_query in abbreviation:
            prioritized_political_parties.append(political_party)
        else:
            other_political_parties.append(political_party)

    # Combine prioritized and other political parties, ensuring all matches are returned
    sorted_political_parties = prioritized_political_parties + other_political_parties

    political_party_suggestions = []
    for political_party in sorted_political_parties:
        political_party_dict = {
            "id": political_party.id,
            "abbreviation": political_party.abbreviation,
            "image_url": political_party.image_url,
            "full_name": political_party.full_name,
            "category": "Partid politic"
        }
        political_party_suggestions.append(political_party_dict)

    return political_party_suggestions

def query_cities(query):
    normalized_query = normalize_string(query).lower()
    query_parts = normalized_query.split()

    if not query_parts:
        return []

    filters = [
        func.unaccent(func.lower(City.name)).ilike(f'%{part}%')
        for part in query_parts
    ]

    query_filter = and_(*filters)
    cities = City.query.filter(query_filter).all()

    prioritized_cities = []
    other_cities = []

    for city in cities:
        name = city.name.lower()
        if normalized_query in name:
            prioritized_cities.append(city)
        else:
            other_cities.append(city)

    sorted_cities = prioritized_cities + other_cities

    city_suggestions = []
    for city in sorted_cities:
        city_dict = {
            "id": city.id,
            "name": city.name,
            "image_url": city.image_url,
            "population": city.population,
            "category": "Oraș"
        }
        city_suggestions.append(city_dict)

    return city_suggestions

def query_tags(query):
    normalized_query = normalize_string(query).lower()
    query_parts = normalized_query.split()

    if not query_parts:
        return []

    filters = [
        func.unaccent(func.lower(Tag.tag_text)).ilike(f'%{part}%')
        for part in query_parts
    ]

    query_filter = and_(*filters)
    tags = Tag.query.filter(query_filter).all()

    prioritized_tags = []
    other_tags = []

    for tag in tags:
        tag_text = tag.tag_text.lower()
        if normalized_query in tag_text:
            prioritized_tags.append(tag)
        else:
            other_tags.append(tag)

    sorted_tags = prioritized_tags + other_tags

    tags_suggestions = []
    for tag in sorted_tags:
        tag_dict = {
            "id": tag.id,
            "tag_text": tag.tag_text,
            "category": "Tag"
        }
        tags_suggestions.append(tag_dict)

    return tags_suggestions

def query_elections(query):
    normalized_query = normalize_string(query).lower()
    query_parts = normalized_query.split()

    if not query_parts:
        return []

    filters = [
        func.unaccent(func.lower(Election.name)).ilike(f'%{part}%')
        for part in query_parts
    ]

    query_filter = and_(*filters)
    elections = Election.query.filter(query_filter).all()

    prioritized_elections = []
    other_elections = []

    for election in elections:
        name = election.name.lower()
        if normalized_query in name:
            prioritized_elections.append(election)
        else:
            other_elections.append(election)

    sorted_elections = prioritized_elections + other_elections

    election_suggestions = []
    for election in sorted_elections:
        election_dict = {
            "id": election.id,
            "name": election.name,
            "image_url": election.image_url,
            "date": election.date,
            "category": "Alegeri"
        }
        election_suggestions.append(election_dict)

    return election_suggestions

def query_sources(query):
    normalized_query = normalize_string(query).lower()
    query_parts = normalized_query.split()

    if not query_parts:
        return []

    filters = [
        func.unaccent(func.lower(Source.name)).ilike(f'%{part}%')
        for part in query_parts
    ]

    query_filter = and_(*filters)
    sources = Source.query.filter(query_filter).all()

    prioritized_sources = []
    other_sources = []

    for source in sources:
        name = source.name.lower()
        if normalized_query in name:
            prioritized_sources.append(source)
        else:
            other_sources.append(source)

    sorted_sources = prioritized_sources + other_sources

    source_suggestions = []
    for source in sorted_sources:
        source_dict = {
            "id": source.id,
            "name": source.name,
            "image_url": source.image_url,
            "category": "Sursă"
        }
        source_suggestions.append(source_dict)

    return source_suggestions

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

