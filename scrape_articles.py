import json
import random
import re
import string
import unicodedata
from flask import jsonify
import requests
import psycopg2
from bs4 import BeautifulSoup
import datetime
import warnings
from fuzzywuzzy import fuzz
from unidecode import unidecode
from urllib3.exceptions import InsecureRequestWarning
from tries.predict import predict_label, tokenizer, model
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent results
DetectorFactory.seed = 0

warnings.filterwarnings("ignore", category=InsecureRequestWarning)


### UTILS ###

def create_db_connection():
    connection = psycopg2.connect(
        dbname="Licenta",
        user="postgres",
        password="password",
        host="localhost"
    )
    return connection

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

def get_random_user_agent():
    return random.choice(user_agents)

def is_published_this_year(parsed_published_date):
    current_year = datetime.datetime.now().year
    return parsed_published_date.year == current_year

def get_latest_article_date(source_name, cur):
    cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
    source_id_result = cur.fetchone()
    
    if source_id_result:
        source_id = source_id_result[0]
        
        cur.execute("""
            SELECT MAX(published_date) FROM articles WHERE source = %s
        """, (source_id,))
        latest_date = cur.fetchone()[0]
        
        return latest_date
    else:
        raise ValueError(f"Source {source_name} not found in sources table.")

def remove_image_dimensions(image_url):
    return re.sub(r'\b(w|h)=\d+\b', '', image_url)

def parse_published_date(published_date_str):
    months = {
        'Ianuarie': 'January', 'Februarie': 'February', 'Martie': 'March', 'Aprilie': 'April',
        'Mai': 'May', 'Iunie': 'June', 'Iulie': 'July', 'August': 'August',
        'Septembrie': 'September', 'Octombrie': 'October', 'Noiembrie': 'November', 'Decembrie': 'December'
    }

    parts = published_date_str.split(', ')
    if len(parts) >= 3:
        day_month_year = parts[1].split()

        time_parts = parts[2].split()
        if len(time_parts) >= 2:
            time = time_parts[1]
        else:
            time = time_parts[0]

        if len(day_month_year) >= 3:
            day = int(day_month_year[0])
            month = months.get(day_month_year[1])
            year = int(day_month_year[2])

            if month:
                datetime_obj = datetime.datetime(year, list(months.values()).index(month) + 1, day, int(time.split(':')[0]), int(time.split(':')[1]))
                return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

    return None

def extract_number_from_string(text):
    numbers = re.findall(r'\d+', text)
    return ''.join(numbers)

def extract_date_and_title(title_with_date):
    parts = title_with_date.split(' - ', 1)
    if len(parts) == 1:
        return None, parts[0]
    date_str = parts[0]
    title = parts[1]
    return date_str, title

def is_text_english(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except LangDetectException:
        return False



### NEXT PAGE ###

def get_next_page_ziaredotcom(soup):
    pagination = soup.find('ul', class_='pagination')
    if pagination:
        disabled_page = pagination.find('li', class_='disabled')
        if disabled_page:
            next_page_link = disabled_page.find_next_sibling('li')
            if next_page_link:
                next_page_url = next_page_link.find('a')['href']
                return next_page_url
    return None

def get_next_page_digi24(soup):
    pagination = soup.find('div', class_='col-6 col-center')
    if pagination:
        disabled_page = pagination.find('a', class_='pagination-link pagination-link-current')
        if disabled_page:
            next_page_link = disabled_page.find_next_sibling('a')
            if next_page_link:
                next_page_url = "https://www.digi24.ro" + next_page_link['href']
                return next_page_url
    return None

def get_next_page_mediafax(current_page_url):
    if '/page/' in current_page_url:
        url_parts = current_page_url.split('/')
        page_number = int(url_parts[-2])
        next_page_number = page_number + 1
        url_parts[-2] = str(next_page_number)
        next_page_url = '/'.join(url_parts)
    else:
        next_page_url = current_page_url.rstrip('/') + '/page/2/'

    return next_page_url

def get_next_page_protv(current_page_url):
    base_url = "https://stirileprotv.ro/stiri/politic/"
    if current_page_url == base_url:
        return base_url + "?page=2"
    elif "?page=" in current_page_url:
        current_page = int(current_page_url.split("=")[-1])
        next_page = current_page + 1
        return base_url + f"?page={next_page}"
    else:
        return None

def get_next_page_adevarul(current_page_url):
    if current_page_url.endswith('.html'):
        parts = current_page_url.split('/')
        page_number_index = parts.index('politica') + 1
        current_page_number = int(parts[page_number_index].split('.')[0])

        next_page_number = current_page_number + 1
        parts[page_number_index] = str(next_page_number) + '.html'
        next_page_url = '/'.join(parts)
    else:
        next_page_url = current_page_url + '/2.html'
    
    return next_page_url

def get_next_page_observator(current_page_url):
    if "?p=" in current_page_url:
        current_page_number = int(current_page_url.split("?p=")[1])
        next_page_number = current_page_number + 1
        next_page_url = current_page_url.split("?p=")[0] + f"?p={next_page_number}"
    else:
        next_page_url = current_page_url + "?p=2"
    
    return next_page_url

def get_next_page_hotnews(current_page_url):
    if 'page/' in current_page_url:
        # Extract the current page number and increment it
        current_page_number = int(current_page_url.rstrip('/').rsplit('/', 1)[-1])
        next_page_number = current_page_number + 1
        next_page_url = current_page_url.rsplit('/', 1)[0] + '/' + str(next_page_number)
    else:
        # Append the 'page/2' to the URL if it's the first page
        if current_page_url.endswith('/'):
            next_page_url = current_page_url + 'page/2'
        else:
            next_page_url = current_page_url + '/page/2'
    return next_page_url

def get_next_page_stiripesurse_and_gandul(current_page_url):
    parts = current_page_url.split("/")
    page_index = parts.index("page")
    page_number = int(parts[page_index + 1])
    next_page_number = page_number + 1
    parts[page_index + 1] = str(next_page_number)
    next_page_url = "/".join(parts)
    return next_page_url

def get_next_page_bursa(buttons):
    num_buttons = len(buttons)
    if num_buttons == 1:
        return "https://www.bursa.ro" + buttons[0]['href']
    elif num_buttons >= 2:
        return "https://www.bursa.ro" + buttons[1]['href']
    else:
        return None

def get_next_page_url_antena3(current_url):
    parts = current_url.split('/')
    for i, part in enumerate(parts):
        if part.startswith('pagina-'):
            page_number_index = i
            break
    current_page_number = int(parts[page_number_index].split('-')[-1])
    next_page_number = current_page_number + 1
    parts[page_number_index] = f'pagina-{next_page_number}'
    next_page_url = '/'.join(parts)
    return next_page_url



### TAGS ###

def filter_and_normalize_tag(tag):
    tag = tag.lower()
    tag = tag.translate(str.maketrans('ăâîșț', 'aaist'))
    tag = unicodedata.normalize('NFKD', tag).encode('ASCII', 'ignore').decode('utf-8')
    tag = re.sub(r'[^a-zA-Z0-9\s]', '', tag)  # Remove special characters
    tag = tag.strip()  # Remove any leading/trailing whitespace
    return tag

def match_tags_to_entities(tags, article_id, published_date, cur, conn):
    unmatched_tags = []
    for tag in tags:
        entity_id = None
        tag_words = tag.split()
        for word in tag_words:
            entity_id, table_name = match_word_to_entities(word, cur)
            if entity_id:
                insert_tag_and_entity(tag, entity_id, table_name, article_id, cur, conn, published_date)
                break
            elif is_election_tag(tag):
                entity_id = match_election(tag)
                insert_tag_and_entity(tag, entity_id, 'elections', article_id, cur, conn, published_date)
                break
        if not entity_id:
            unmatched_tags.append(tag)
    
    if unmatched_tags:
        insert_unmatched_tags(unmatched_tags, article_id, cur, conn)

def is_election_tag(tag):
    election_keywords = ['alegeri', 'alegerile', 'alegerilor', 'rezultate', 'sondaje', 'sondaj' , 'europarlamentare', 'locale', 'prezidentiale', 'parlamentare']
    return any(keyword in tag.lower() for keyword in election_keywords)

def match_election(tag):
    if 'europarlamentare' in tag.lower():
        return 2
    elif 'locale' in tag.lower():
        return 3
    elif 'prezidentiale' in tag.lower():
        return 4
    elif 'parlamentare' in tag.lower():
        return 5
    else:
        return 1

def match_word_to_entities(word, cur):
    def normalized_similarity(string1, string2):
        return fuzz.ratio(unidecode(string1.lower()), unidecode(string2.lower()))

    cur.execute("SELECT id, last_name FROM politicians")
    politicians = cur.fetchall()
    for politician_id, last_name in politicians:
        if normalized_similarity(word, last_name) > 80:
            return politician_id, 'politicians'
    
    cur.execute("SELECT id, name FROM cities")
    cities = cur.fetchall()
    for city_id, name in cities:
        if normalized_similarity(word, name) > 80:
            return city_id, 'cities'

    cur.execute("SELECT id, abbreviation FROM political_parties")
    political_parties = cur.fetchall()
    for party_id, abbreviation in political_parties:
        if normalized_similarity(word, abbreviation) > 80:
            return party_id, 'political_parties'
    
    return None, None

def insert_tag_and_entity(tag, entity_id, table_name, article_id, cur, conn, published_date):
    cur.execute("""
        SELECT id
        FROM tags
        WHERE tag_text = %s
    """, (tag,))
    result = cur.fetchone()
    
    cur.execute("""
        INSERT INTO tags (article_id, tag_text)
        VALUES (%s, %s)
        RETURNING id
    """, (article_id, tag))
    tag_id = cur.fetchone()[0]


    if not result:
        if table_name == "politicians":
            cur.execute("""
                INSERT INTO tag_politician (tag_id, politician_id)
                VALUES (%s, %s)
            """, (tag_id, entity_id))
        elif table_name == "cities":
            cur.execute("""
                INSERT INTO tag_city (tag_id, city_id)
                VALUES (%s, %s)
            """, (tag_id, entity_id))
        elif table_name == "political_parties":
            cur.execute("""
                INSERT INTO tag_political_parties (tag_id, political_party_id)
                VALUES (%s, %s)
            """, (tag_id, entity_id))
        elif table_name == "elections":
            cur.execute("""
                INSERT INTO tag_election (tag_id, election_id)
                VALUES (%s, %s)
            """, (tag_id, entity_id))

    conn.commit()

def insert_unmatched_tags(unmatched_tags, article_id, cur, conn):
    for tag_text in unmatched_tags:
        cur.execute("""
            SELECT id, count
            FROM tags
            WHERE tag_text = %s
        """, (tag_text,))
        result = cur.fetchone()

        if result:
            tag_id, count = result
            cur.execute("""
                UPDATE tags
                SET count = count + 1
                WHERE id = %s
            """, (tag_id,))
            conn.commit()
        else:
            cur.execute("""
                INSERT INTO tags (article_id, tag_text, count)
                VALUES (%s, %s, %s)
            """, (article_id, tag_text, 1))
            conn.commit()

def normalize_and_remove_diacritics(text):
    normalized_text = unicodedata.normalize('NFC', text)
    diacritic_map = {
        'ă': 'a', 'Ă': 'A',
        'â': 'a', 'Â': 'A',
        'î': 'i', 'Î': 'I',
        'ș': 's', 'Ș': 'S',
        'ț': 't', 'Ț': 'T',
    }
    for diacritic, letter in diacritic_map.items():
        normalized_text = normalized_text.replace(diacritic, letter)
    return normalized_text

def extract_uppercase_word_groups(text):
    normalized_text = normalize_and_remove_diacritics(text)
    pattern1 = r'\b[A-ZȘȚÂÎ][a-zșțâî]{2,}\b(?:\s+[A-ZȘȚÂÎ][a-zșțâî]{2,}\b)*'
    pattern2 = r'\b[A-ZȘȚÂÎ][a-zșțâî]*\b\s+\d+'
    pattern3 = r'\b[A-ZȘȚÂÎ]{2,}\b'
    pattern4 = r'\b[A-ZȘȚÂÎ][a-zșțâî]{2,}\b'
    regex1 = re.compile(pattern1, re.UNICODE)
    regex2 = re.compile(pattern2, re.UNICODE)
    regex3 = re.compile(pattern3, re.UNICODE)
    regex4 = re.compile(pattern4, re.UNICODE)
    matches1 = regex1.findall(normalized_text)
    matches2 = regex2.findall(normalized_text)
    matches3 = regex3.findall(normalized_text)
    matches4 = regex4.findall(normalized_text)
    all_matches = set(matches1 + matches2 + matches3 + matches4)
    filtered_matches = set()
    for tag in all_matches:
        if len(tag.split()) > 1:
            is_subset = any(tag in multi_tag.split() for multi_tag in all_matches if multi_tag != tag)
            if not is_subset:
                filtered_matches.add(tag)
        else:
            if not any(tag in multi_tag.split() for multi_tag in all_matches if multi_tag != tag):
                filtered_matches.add(tag)
    return filtered_matches



### SCRAPPING ###

def extract_article_id_ziaredotcom(article_url):
    segments = article_url.split('/')
    last_segment = segments[-1]
    match = re.search(r'\d+$', last_segment)
    if match:
        article_id = match.group(0)
        return article_id
    else:
        return None

def scrape_article_ziaredotcom(article_url, title):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        author_div = soup.find('div', class_='news__author')
        author_name = author_div.span.get_text(strip=True)

        number_of_views = soup.find('div', class_='news__views').text.strip()

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        tags_div = soup.find('div', class_='tags__container article__marker')
        if tags_div:
            article_tags = [filter_and_normalize_tag(tag.get_text(strip=True)) for tag in tags_div.find_all('a')]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        img_tag = soup.find('a', class_='news__image').find('img')
        image_url_with_dimensions = img_tag['src']
        image_url = remove_image_dimensions(image_url_with_dimensions)

        content_div = soup.find('div', class_='news__content descriere_main article__marker')
        p_elements = content_div.find_all('p')
        article_text = [p.get_text(strip=True) for p in p_elements[:-2] if p.get_text(strip=True) != '']

        comments = scrape_comments_ziaredotcom(extract_article_id_ziaredotcom(article_url))

        return {
            'url': article_url,
            'author': author_name,
            'number_of_views': number_of_views,
            'tags': tags,
            'image_url': image_url,
            'article_text': article_text,
            'comments': comments
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_comments_ziaredotcom(article_id):
    ajax_url = f"https://ziare.com/index.php?module=loadAllComments.ajxinternal&newsId={article_id}"
    response = requests.get(ajax_url)
    if response.status_code == 200:
        comments_data = response.json()
        soup = BeautifulSoup(comments_data, 'html.parser')
        comments_divs = soup.find_all('div', class_='comments__text')
        comments = [comment.get_text(strip=True) for comment in comments_divs]
        return comments
    else:
        print("Failed to fetch comments")
        return []

def scrape_ziaredotcom():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Ziare.com'
    url = "https://ziare.com/politica/stiri-politice/stiri/"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = soup.find_all('div', class_='title__article')
            for link in article_links:
                a_element = link.find('a')
                a_text = a_element.get_text(strip=True)
                published_date, title = extract_date_and_title(a_text)
                if published_date is not None:
                    parsed_published_date = parse_published_date(published_date)
                    parsed_published_date = datetime.datetime.strptime(parsed_published_date, '%Y-%m-%d %H:%M:%S')
                    if is_published_this_year(parsed_published_date):
                        if latest_article_date is not None and parsed_published_date <= latest_article_date:
                            stop_scraping = True
                            print("Ziare.com - UPDATED.")
                            break
                        article_url = link.a['href']
                        article_data = scrape_article_ziaredotcom(article_url, title)
                        if article_data:
                            content = f"{title} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                            emotion_label = predict_label(content, tokenizer, model)
                            
                            cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                            source_id_result = cur.fetchone()
                            source_id = source_id_result[0]
                                
                            cur.execute("""
                                INSERT INTO articles (title, url, author, published_date, number_of_views, image_url, source, emotion)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                title,
                                article_data['url'],
                                article_data['author'],
                                parsed_published_date,
                                extract_number_from_string(article_data.get('number_of_views', 0)),
                                article_data['image_url'],
                                source_id,
                                emotion_label
                            ))
                            conn.commit()

                            cur.execute("SELECT id FROM articles WHERE url = %s", (article_data['url'],))
                            article_id = cur.fetchone()[0]

                            for paragraph_text in article_data['article_text']:
                                cur.execute("""
                                    INSERT INTO article_paragraphs (article_id, paragraph_text)
                                    VALUES (%s, %s)
                                """, (article_id, paragraph_text))
                                conn.commit()

                            match_tags_to_entities(article_data['tags'], article_id, parsed_published_date, cur, conn)
                            
                            for comment_text in article_data['comments']:
                                cur.execute("""
                                    INSERT INTO comments (article_id, comment_text)
                                    VALUES (%s, %s)
                                """, (article_id, comment_text))
                                conn.commit()
                            print(f"\n{source_name} INSERTED.\n")
                        else:
                            print("Failed to scrape article:", article_url)
                    else:
                        stop_scraping = True
                        break
            url = get_next_page_ziaredotcom(soup)
            if url is None:
                stop_scraping = True
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

def extract_author_name(link):
    author_name = link.replace('/autor/', '')
    author_name = author_name.replace('-', ' ').title()
    return author_name

def scrape_article_digi24(article_url, title):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        author_div = soup.find_all('div', class_='entry data-app-meta data-app-meta-article')[-1].find_all('a')
        if author_div and len(author_div) >= 2:
            last_author_link = author_div[-1]
            if 'href' in last_author_link.attrs and 'autor' in last_author_link['href']:
                author_link = last_author_link['href']
                author_name = extract_author_name(author_link)
            else:
                author_name = "Unknown"
        else:
            author_name = "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        tag_elements = soup.find('ul', class_='tags-list')
        if tag_elements:
            tag_links = tag_elements.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.get_text(strip=True)) for tag in tag_links]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        date_elements = soup.find('div', class_='author-meta')
        second_span_element = date_elements.find_all('span')[-1]
        published_date_text = second_span_element.text.strip()
        first_digit_index = next((i for i, c in enumerate(published_date_text) if c.isdigit()), None)
        published_date_str = published_date_text[first_digit_index:]
        published_date = datetime.datetime.strptime(published_date_str, '%d.%m.%Y %H:%M')

        figure_element = soup.find('figure', class_='article-thumb')
        img_element = figure_element.find('img')
        image_url_with_dimensions = img_element['src']
        image_url = remove_image_dimensions(image_url_with_dimensions)

        content_div = soup.find('div', class_='entry data-app-meta data-app-meta-article')
        p_elements = content_div.find_all('p', attrs={'data-index': True})
        article_text = [p.get_text(strip=True) for p in p_elements]

        return {
            'author': author_name,
            'published_date': published_date,
            'image_url': image_url,
            'tags': tags,
            'article_text': article_text
        }
    else:
        print("Failed to scrape article:", article_url)

def clean_title_digi24(title):
    pattern = r'([a-zA-Z]+[a-z])([A-Z].*)'
    match = re.match(pattern, title)
    if match:
        modified_title = match.group(2).strip()
        return modified_title
    else:
        return title.strip()

def scrape_digi24():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Digi24'
    url = "https://www.digi24.ro/stiri/actualitate/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = soup.find_all('h2', class_='h4 article-title')
            for link in article_links:
                a_element = link.find('a')
                article_url = "https://www.digi24.ro" + a_element['href']
                unfiltered_title = a_element.get_text(strip=True)
                title = clean_title_digi24(unfiltered_title)
                article_data = scrape_article_digi24(article_url, title)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nDigi24 - UPDATED.\n")
                            break

                        content = f"{title} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]
                        
                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            article_data['published_date'],
                            article_data['image_url'],
                            source_id,
                            emotion_label
                        ))
                        conn.commit()
                        
                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]
                        
                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()
                        
                        match_tags_to_entities(article_data['tags'], article_id, article_data['published_date'], cur, conn)
                        
                        print(f"\n{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_digi24(soup)
            if url is None:
                stop_scraping = True
            # else:
            #     print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

def check_if_updated_mediafax(url, cur):
    latest_article_date = get_latest_article_date("Mediafax", cur)
    print(latest_article_date)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_list = soup.find('ul', class_='intros')
        article_links = article_list.select(
            'a.title:not([title="UPDATE"]):not([title="LIVE TEXT"]):not([title="VIDEO"]):not([title="BREAKING NEWS"])')
        for link in article_links:
            article_url = link['href']
            title = link.get_text(strip=True)
            article_data = scrape_article_mediafax(article_url, title)
            if article_data:
                published_date = article_data['published_date']
                if latest_article_date is not None and published_date <= latest_article_date:
                    return True
    return False

def scrape_article_mediafax(article_url, title):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        a_element = soup.find('a', class_='author_link')
        if a_element:
            author_name = a_element.text.strip()
        else:
            author_name = "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        dl_element = soup.find('dl', class_='a-tags')
        if dl_element:
            dd_elements = dl_element.find_all('dd')
            article_tags = [filter_and_normalize_tag(dd.get_text(strip=True))  for dd in dd_elements]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        views_extracted = soup.find('span', class_='views')
        if views_extracted:
            views_text = views_extracted.get_text(strip=True)
            number_of_views = extract_number_from_string(views_text)
        else:
            number_of_views = 0

        date_element = soup.find('dd', class_='date')
        date_text = date_element.get_text()
        cleaned_date_text = ''.join(filter(str.isdigit, date_text))
        published_date = datetime.datetime.strptime(cleaned_date_text, '%d%m%Y%H%M')

        article_text_content_div = soup.find('div', id='article_text_content')
        content_div = article_text_content_div.find('div', class_='just-article-content')
        article_text = [p.get_text(strip=True) for p in content_div.find_all('p')]

        image_div = soup.find('div', class_='ArticleImageContainer')
        if image_div and image_div.find('img'):
            image_url_with_dimensions = image_div.find('img')['data-src']
            image_url = remove_image_dimensions(image_url_with_dimensions)
        else:
            image_url = None

        return {
            'author': author_name,
            'published_date': published_date,
            'tags': tags,
            'number_of_views': number_of_views,
            'article_text': article_text,
            'image_url': image_url
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_mediafax():
    conn = create_db_connection()
    cur = conn.cursor()
    base_url = "https://www.mediafax.ro/politic/arhiva/"
    current_date = datetime.datetime.now()
    current_month = current_date.month
    month_url = f"{base_url}2024/{current_month:02d}"
    print(month_url)
    if check_if_updated_mediafax(month_url, cur):
        print("\nMediaFax - UPDATED.\n")
    else:
        for month in range(current_month, 0, -1):
            month_url = f"{base_url}2024/{month:02d}"
            print(f"Scraping articles from: {month_url}")
            scrape_articles_from_month_mediafax(month_url, cur, conn)

def scrape_articles_from_month_mediafax(month_url, cur, conn):
    stop_scraping = False
    while not stop_scraping:
        response = requests.get(month_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_list = soup. find('ul', class_='intros')
            if not article_list:
                break
            article_links = article_list.select('a.title:not([title="UPDATE"]):not([title="LIVE TEXT"]):not([title="VIDEO"]):not([title="BREAKING NEWS"]):not([title="BREAKING"])')
            for link in article_links:
                article_url = link['href']
                title = link.get_text(strip=True)
                article_data = scrape_article_mediafax(article_url, title)
                if article_data:

                    if len(article_data['article_text']) > 1:
                        content = f"{title} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                    else:
                        content = f"{title} {article_data['article_text'][0]}"
                    emotion_label = predict_label(content, tokenizer, model)

                    source_name = 'Mediafax'
                    cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                    source_id_result = cur.fetchone()
                    source_id = source_id_result[0]

                    cur.execute("""
                        INSERT INTO articles (title, url, author, number_of_views, published_date, image_url, source, emotion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        title,
                        article_url,
                        article_data['author'],
                        article_data['number_of_views'],
                        article_data['published_date'],
                        article_data['image_url'],
                        source_id, 
                        emotion_label
                    ))
                    conn.commit()

                    cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                    article_id = cur.fetchone()[0]

                    for paragraph_text in article_data['article_text']:
                        cur.execute("""
                            INSERT INTO article_paragraphs (article_id, paragraph_text)
                            VALUES (%s, %s)
                        """, (article_id, paragraph_text))
                        conn.commit()

                    match_tags_to_entities(article_data['tags'], article_id, article_data['published_date'], cur, conn)

                    print(f"\n{source_name} INSERTED.\n")
                else:
                    print("Failed to scrape article:", article_url)
            month_url = get_next_page_mediafax(month_url)
            print("\nPAGE CHANGED.\n", month_url)
            if month_url is None:
                stop_scraping = True
        else:
            print("Failed to fetch page:", month_url)

def scrape_article_protv(article_url, title):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        author_div = soup.find('div', class_='author--name')
        if author_div:
            author_link = author_div.find('a')
            if author_link:
                author_name = author_link.text.strip()
            else:
                author_name = author_div.text.strip()
        else:
            author_name = "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        second_p = soup.find('div', class_='article--info').find_all('p')[1]
        if second_p:
            tag_links = second_p.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        image_element = soup.find('img', class_='article-picture img-fluidi')
        if image_element:
            image_url_with_dimensions = image_element['src']
            image_url = remove_image_dimensions(image_url_with_dimensions)
        else: 
            image_url = None 

        third_p = soup.find('div', class_='article--info').find_all('p')[2]
        date_string = third_p.get_text(strip=True).replace('Dată publicare:', '').strip()
        published_date = datetime.datetime.strptime(date_string, '%d-%m-%Y %H:%M')

        content_div = soup.find('div', class_='article--text')
        paragraphs = content_div.find_all('p')[:-3]
        article_text = [p.get_text(strip=True) for p in paragraphs]

        return {
            'author': author_name,
            'published_date': published_date,
            'tags': tags,
            'article_text': article_text,
            'image_url': image_url
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_protv():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'PROTV'
    url = "https://stirileprotv.ro/stiri/politic/"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', class_='grid article')
            for article in articles:
                title_div = article.find('div', class_='article-title')
                title_a = title_div.find('a')
                title = title_a.get_text(strip=True)
                article_url = title_a['href']
                image_div = article.find('picture', class_='article-img')

                backup_image_with_dimensions = image_div.find('img')['data-src']
                backup_image = remove_image_dimensions(backup_image_with_dimensions)

                article_data = scrape_article_protv(article_url, title)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nPROTV - UPDATED.\n")
                            break
                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        content = f"{title} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        print(f"\n{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_protv(url)
            if url is None:
                stop_scraping = True
            # else:
            #     print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

def clean_title_adevarul(title):
    extra_words = ['SURSE', 'EXCLUSIV', 'DETALII', 'FOTO', 'VIDEO']
    cleaned_title = ''
    word_buffer = ''
    for char in title:
        if char in string.whitespace or char in string.punctuation:
            if word_buffer.upper() not in extra_words:
                cleaned_title += word_buffer
            word_buffer = ''
            cleaned_title += char
        else:
            word_buffer += char

    if word_buffer.upper() not in extra_words:
        cleaned_title += word_buffer

    cleaned_title = cleaned_title.rstrip(string.punctuation)

    return cleaned_title.strip()

def scrape_article_adevarul(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        unfiltered_title = soup.find('h1', class_='titleAndHeadings svelte-hvtg27').text.strip()
        title = clean_title_adevarul(unfiltered_title)

        img_div = soup.find('img', class_='svelte-h45upf')
        image_url_with_dimensions = img_div['src']
        image_url = remove_image_dimensions(image_url_with_dimensions)

        author_span = soup.find('div', class_='authors metaFont svelte-hvtg27')
        if author_span:
            author_name = author_span.find('a').text.strip()
        else:
            author_name = "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        tags_div = soup.find('div', class_='tags svelte-1kju2ho')
        if tags_div:
            a_tags = tags_div.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.get_text()) for tag in a_tags]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        time_element = soup.find('time', class_='svelte-hvtg27')
        datetime_str = time_element['datetime']
        datetime_str_with_offset = datetime_str[:-1] + "+0000"
        published_date_long_format = datetime.datetime.strptime(datetime_str_with_offset, "%Y-%m-%dT%H:%M:%S.%f%z")
        string_published_date = published_date_long_format.strftime('%d-%m-%Y %H:%M')
        published_date = datetime.datetime.strptime(string_published_date, '%d-%m-%Y %H:%M')

        main_element = soup.find('main', class_='svelte-1m9guhq')
        article_text = [p.get_text(strip=True) for p in main_element.find_all('p')]

        comments = scrape_comments_adevarul(extract_article_id_adevarul(article_url))
            
        return {
            'title': title,
            'author': author_name,
            'published_date': published_date,
            'tags': tags,
            'image_url': image_url,
            'comments': comments,
            'article_text': article_text
        }
    else:
        print("Failed to scrape article:", article_url)

def extract_article_id_adevarul(article_url):
    try:
        last_part = article_url.split('/')[-1]
        id_part = last_part.split('.html')[0]
        article_id = ''.join(filter(str.isdigit, id_part))
        return article_id
    except Exception as e:
        print("Error extracting article ID:", e)
        return None

def scrape_comments_adevarul(article_id):
    all_comment_texts = []
    offset = 0
    while True:
        url = f"https://social.adh.reperio.news/adevarul.ro/comment/content/{article_id}?offset={offset}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            comments = data.get('comments', [])
            if not comments:
                break
            for comment in comments:
                all_comment_texts.append(comment['text'])
            offset += len(comments)
        else:
            print("Failed to fetch comments. Status code:", response.status_code)
            break
    return all_comment_texts

def scrape_adevarul():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Adevărul'
    url = "https://adevarul.ro/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            rest_of_the_articles_div = soup.find('div', id='b-d3739cf7-fa12-475d-bccc-856eb0f20b50')
            rest_links = rest_of_the_articles_div.find_all('a', class_='row summary svelte-1mo6hi5 small')

            if url == "https://adevarul.ro/politica":
                first_part = soup.find('div', id='b-489c850e-0c7f-40e3-a26d-3094036072a2')
                first_part_links = first_part.find_all('a', class_='row summary svelte-1mo6hi5 small')
                all_links = rest_links + first_part_links
            else:
                all_links = rest_links

            for article_url in all_links:
                article_data = scrape_article_adevarul(article_url['href'])
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nAdevarul - UPDATED.\n")
                            break

                        content = f"{article_data['title']} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url['href'],
                            article_data['author'],
                            published_date,
                            article_data['image_url'],
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url['href'],))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        for comment_text in article_data['comments']:
                            cur.execute("""
                                INSERT INTO comments (article_id, comment_text)
                                VALUES (%s, %s)
                            """, (article_id, comment_text))
                            conn.commit()
                        print(f"{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)
            url = get_next_page_adevarul(url)
            if url is None:
                stop_scraping = True
            # print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

def scrape_article_observator(article_url, title):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        author_span = soup.find('span', class_='headline-link')
        if author_span:
            author = author_span.get_text(strip=True)
        else:
            author = "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        tags_div = soup.find('div', class_='taguri')
        if tags_div:
            tag_links = tags_div.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        image_element = soup.find('div', class_="media-top").find('img', class_="lazy wow fadeIn")
        if image_element:
            image_url_with_dimensions = image_element['data-src']
            image_url = remove_image_dimensions(image_url_with_dimensions)
        else: 
            image_url = None

        published_date_str = soup.find('div', class_='headline-time').find('p').get_text(strip=True)
        date_and_time_parts = published_date_str.split(',')
        date_part = date_and_time_parts[0][3:].strip()
        time_part = date_and_time_parts[1].strip()
        date_obj = datetime.datetime.strptime(date_part, "%d.%m.%Y")
        time_obj = datetime.datetime.strptime(time_part, "%H:%M")
        published_date = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, time_obj.hour, time_obj.minute)

        first_p = soup.find('div', class_='header-cnt').find('p').get_text(strip=True)
        normalized_first_p = unicodedata.normalize("NFKD", first_p)
        rest_of_paragraphs_div = soup.find('div', class_='center-cnt')
        rest_of_paragraphs = rest_of_paragraphs_div.find_all('p')
        non_class_paragraphs = [p.get_text(strip=True) for p in rest_of_paragraphs if not p.has_attr('class')]
        article_text = [normalized_first_p] + non_class_paragraphs

        return {
            'author': author,
            'published_date': published_date,
            'tags': tags,
            'article_text': article_text,
            'image_url': image_url
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_observator():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Observator'
    url = "https://observatornews.ro/politic/"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            section = soup.find('section', class_='stiri')
            articles = section.find_all('div', class_='stire')
            for article in articles:
                article_a_element = article.find('a', class_='full-link')
                title = article_a_element.get_text(strip=True)
                backup_image_with_dimensions = article.find('img')['data-src']
                backup_image = remove_image_dimensions(backup_image_with_dimensions)
                article_url = article_a_element['href']
                article_data = scrape_article_observator(article_url, title)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nObservator - UPDATED.\n")
                            break
                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        content = f"{title} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        print(f"{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_observator(url)
            if url is None:
                stop_scraping = True
            # else:
            #     print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

### nu are tags naturale, comments nu mai merg
def scrape_article_hotnews(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('article', class_='article-single-page')

        if not main_div:
            print("Failed to scrape article:", article_url)
            return

        title = main_div.find('h1', class_='entry-title').text.strip()
        unwanted_words = ["VIDEO", "GRAFICĂ INTERACTIVĂ"]
        for word in unwanted_words:
            title = title.replace(word, "").strip()

        img_div = main_div.find('img', class_='article-single-featured-image')
        image_url_with_dimensions = img_div['src']
        image_url = remove_image_dimensions(image_url_with_dimensions)

        author_span = main_div.find('li', class_='author vcard')
        author_name = author_span.text.strip() if author_span else "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]

        unparsed_published_date = main_div.find('time', class_='entry-date published')
        published_date_str = unparsed_published_date['datetime']
        published_date = datetime.datetime.fromisoformat(published_date_str)

        main_element = main_div.find('div', class_='entry-content')
        article_text = [p.get_text(strip=True) for p in main_element.find_all('p')]


        # Sunt foarte futute comentariile aici
        # comments_div = soup.find('div', id='comments')
        # comments = []
        # if comments_div:
        #     comment_bodies = comments_div.find_all('div', class_='comment-body')
        #     comments = [comment_body.get_text(strip=True) for comment_body in comment_bodies]

        return {
            'title': title,
            'author': author_name,
            'published_date': published_date,
            'tags': list(tags),
            'image_url': image_url,
            # 'comments': comments,
            'article_text': article_text
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_hotnews():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'HotNews'
    url = "https://hotnews.ro/c/actualitate/politic"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_divs = soup.find_all('article', class_='post-has-image')
            links = []
            for article_div in article_divs:
                a_tag = article_div.find('figure').find('a')
                if a_tag:
                    links.append(a_tag['href'])

            for article_url in links:
                article_data = scrape_article_hotnews(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        published_date_naive = published_date.replace(tzinfo=None)
                        if latest_article_date is not None and published_date_naive <= latest_article_date:
                            stop_scraping = True
                            print("\nHotNews - UPDATED.\n")
                            break

                        title = article_data['title']
                        article_text = article_data['article_text']
                        if article_text:
                            if len(article_text) >= 2:
                                content = f"{title} {article_text[0]} {article_text[1]}"
                            elif len(article_text) == 1:
                                content = f"{title} {article_text[0]}"
                            else:
                                content = title
                        else:
                            content = title
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            article_data['image_url'],
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        # for comment_text in article_data['comments']:
                        #     cur.execute("""
                        #         INSERT INTO comments (article_id, comment_text)
                        #         VALUES (%s, %s)
                        #     """, (article_id, comment_text))
                        #     conn.commit()

                        print(f"{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)
            url = get_next_page_hotnews(url)
            if url is None:
                stop_scraping = True
            # print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

def scrape_article_stiripesurse(article_url):
    custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": custom_user_agent}
    response = requests.get(article_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        unfiltered_title_element = soup.select_one('h1.article-single-title-v2, h1.article-single-title')
        if unfiltered_title_element:
            unfiltered_title = unfiltered_title_element.get_text(strip=True)
            words_to_filter = ["VIDEO", "Video"]
            title_words = unfiltered_title.split()
            filtered_words = [word for word in title_words if word not in words_to_filter]
            title = ' '.join(filtered_words)

            if is_text_english(title):
                print("The article title is in English. Skipping the article.")
                return
        else:
            title = "Fara titlu"

        info_div = soup.select_one('div.article-single-meta, div.article-single-meta-v2')
        if info_div:
            unfiltered_author = info_div.find('address').get_text(strip=True)
            author = unfiltered_author.split(',')[0].strip()
        else:
            author = "Necunoscut"

        published_date_str = info_div.find('time').get_text(strip=True)
        published_date = datetime.datetime.strptime(published_date_str, '%d/%m/%Y %H:%M')

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        second_p = soup.find('div', class_='article-tags')
        if second_p:
            tag_links = second_p.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        image_element = soup.find('img', class_='attachment-large')
        if image_element:
            image_url_with_dimensions = image_element['src']
            image_url = remove_image_dimensions(image_url_with_dimensions)
        else: 
            image_url = None 

        content_div = soup.find('section', class_='article-content')
        paragraphs = content_div.find_all('p')
        article_text = [p.get_text(strip=True) for p in paragraphs]
        first_paragraph_div = content_div.find('h3')
        if first_paragraph_div:
            first_paragraph = first_paragraph_div.get_text(strip=True)
            article_text.insert(0, first_paragraph)

        return {
            'title': title,
            'author': author,
            'published_date': published_date,
            'tags': tags,
            'article_text': article_text,
            'image_url': image_url
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_stiripesurse():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Știri pe surse'
    url = "https://www.stiripesurse.ro/politica/page/1"
    custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": custom_user_agent}
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            if url == "https://www.stiripesurse.ro/politica/page/1":
                article_sections = soup.find_all('article', class_='article-category-featured border-politica')
                articles.extend(article_sections)

            rest_of_articles_divs = soup.find_all('div', class_='column ld-one-half md-one-half article-category-container')
            articles.extend(rest_of_articles_divs)
            
            for article in articles:
                article_url = article.find('a')['href']
                
                views_span = article.find('span', class_='views')
                if views_span:
                    number_of_views = views_span.get_text(strip=True)
                else: 
                    number_of_views = 0

                article_data = scrape_article_stiripesurse(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nStiri pe surse - UPDATED.\n")
                            break

                        if len(article_data['article_text']) > 1:
                            content = f"{article_data['title']} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                        else:
                            content = f"{article_data['title']} {article_data['article_text'][0]} "
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, number_of_views, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            number_of_views,
                            article_data['image_url'],
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        print(f"{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_stiripesurse_and_gandul(url)
            if url is None:
                stop_scraping = True
            # else:
            #     print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)
    cur.close()
    conn.close()

def scrape_article_gandul(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1', class_='font-titles').get_text(strip=True)

        author_div = soup.find('div', class_='name')
        if author_div:
            author = author_div.find('a').get_text(strip=True)
        else:
            author = "Unknown"

        published_date_str = soup.find('div', class_='date_published').get_text(strip=True)
        date_time_str = published_date_str.replace('Publicat: ', '').replace(',', '')
        published_date = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M')

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        tags_div = soup.find('div', class_='single__tags mg-bottom-20')
        if tags_div:
            tag_links = tags_div.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        # print("Title:\n", title)
        # print("Tag-uri extrase din titlu:\n", title_tags)
        # print("Tag-uri gasite:\n", article_tags)
        # print("Tag-uri totale:\n", tags)

        image_element = soup.find('div', class_='single__media').findChildren('picture', recursive=False)
        if image_element:
            img_tag = image_element[0].find('img')
            if img_tag:
                image_url = img_tag['src']
            else:
                image_url = None
        else:
            image_url = None

        single_content_div = soup.find('div', class_='single__content')
        article_text = []
        all_elements = single_content_div.find_all(['p', 'blockquote'])
        for element in all_elements:
            if element.name == 'p':
                if element.text.strip():
                    if not element.text.strip().startswith(('Sursa:', 'CITEȘTE ȘI')):
                        article_text.append(element.text.strip())
                    else:
                        break
            elif element.name == 'blockquote':
                article_text.append(element.text.strip())

        return {
            'title': title,
            'author': author,
            'published_date': published_date,
            'tags': tags,
            'article_text': article_text,
            'image_url': image_url
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_gandul():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Gândul'
    url = "https://www.gandul.ro/politica/page/1"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            main_div = soup.find('div', class_='archive__main')

            articles = []
            first_div = main_div.find('div')
            articles.append(first_div)
            
            article_divs = soup.find_all('div', class_='articles mg-top-20 md:articles--3-c articles--rounded')
            for article_div in article_divs:
                article_elements = article_div.find_all('div', class_='article')
                for article_element in article_elements:
                    articles.append(article_element)
            
            for article in articles:
                article_url = article.find('a')['href']
                backup_image = article.find('img')['src']
                article_data = scrape_article_gandul(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nGândul - UPDATED.\n")
                            break

                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        title = article_data['title']
                        article_text = article_data['article_text']
                        if article_text:
                            if len(article_text) >= 2:
                                content = f"{title} {article_text[0]} {article_text[1]}"
                            elif len(article_text) == 1:
                                content = f"{title} {article_text[0]}"
                            else:
                                content = title
                        else:
                            content = title                        
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        print(f"{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_stiripesurse_and_gandul(url)
            if url is None:
                stop_scraping = True
            # else:
            #     print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

def scrape_article_bursa(article_url):
    response = requests.get(article_url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1', class_='post-title').text.strip()

        image_element = soup.find('img', class_='foto_zoom cursor_hand')
        if image_element:
            image_url = "https://www.bursa.ro" + image_element['src']
        else:
            image_url = None

        info_header = soup.find('header', class_='post-header').find('p')
        author_span = info_header.find('span')
        if author_span:
            author_name = author_span.text.strip()
        else:
            author_name = "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        tags_div = soup.find('footer', class_='post-meta').find('p')
        if tags_div:
            a_tags = tags_div.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.get_text()) for tag in a_tags]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        string_published_date = info_header.find_all('span')[1].find('span').text.strip()
        months = {
            'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4,
            'mai': 5, 'iunie': 6, 'iulie': 7, 'august': 8,
            'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12
        }

        parts = string_published_date.split()
        if len(parts) > 1 and '-' in parts[0]:
            day = int(parts[0].split('-')[0])
        else:
            day = int(parts[0])

        month_str = parts[-1].lower()
        month = months.get(month_str)
        current_year = datetime.datetime.now().year
        published_date = datetime.datetime(current_year, month, day)


        div_element = soup.find('div', id='articol-text')
        article_text = [p.get_text(strip=True) for p in div_element.find_all('p')]

        comment_divs = soup.find_all('div', class_='comment-content')
        comments = [div.find('p').get_text(strip=True) for i, div in enumerate(comment_divs) if i % 2 == 1]        
            
        return {
            'title': title,
            'author': author_name,
            'published_date': published_date,
            'tags': tags,
            'image_url': image_url,
            'comments': comments,
            'article_text': article_text
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_bursa():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Bursa'
    url = "https://www.bursa.ro/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            article_links = []
            first_part = soup.find_all('header', class_='caseta-medie-header')
            for header in first_part:
                link = header.find('a')['href']
                article_links.append(link)

            second_part = soup.find_all('header', class_='caseta-medie-1col-header')
            for article in second_part:
                link = article.find('a')['href']
                article_links.append(link)

            for article_url_incomplete in article_links:
                article_url = "https://www.bursa.ro" + article_url_incomplete
                article_data = scrape_article_bursa(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nBursa - UPDATED.\n")
                            break

                        content = f"{article_data['title']} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            article_data['image_url'],
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        for comment_text in article_data['comments']:
                            cur.execute("""
                                INSERT INTO comments (article_id, comment_text)
                                VALUES (%s, %s)
                            """, (article_id, comment_text))
                            conn.commit()
                        print(f"{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)

            buttons = soup.find_all('a', class_='btn btn-primary btn-lg')
            url = get_next_page_bursa(buttons)
            if url is None:
                stop_scraping = True
            # print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()

def scrape_article_antena3(article_url, title):
    custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": custom_user_agent}
    response = requests.get(article_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        image_element = soup.find('img', id='ivm-preroll-image')
        if image_element:
            image_url = image_element['src']
        else:
            image_url = None

        info_spans = soup.find('div', class_='autor-ora-comentarii').find_all('span')
        author_span = info_spans[0]
        if author_span:
            author_name = author_span.find('a')
            if author_name:
                author = author_name.text.strip()
            else:
                author = "Unknown"
        else:
            author = "Unknown"

        raw_title_tags = extract_uppercase_word_groups(title)
        title_tags = [filter_and_normalize_tag(tag) for tag in raw_title_tags]
        tags_div = soup.find('div', class_='tags')
        if tags_div:
            a_tags = tags_div.find_all('a')
            article_tags = [filter_and_normalize_tag(tag.get_text()) for tag in a_tags]
        else:
            article_tags = []
        tags = set(title_tags).union(article_tags)

        if len(info_spans) > 0:
            string_published_date = info_spans[-1].text.strip()
        else:
            string_published_date = None
        months = {
            'Ianuarie': 1, 'Februarie': 2, 'Martie': 3, 'Aprilie': 4,
            'Mai': 5, 'Iunie': 6, 'Iulie': 7, 'August': 8,
            'Septembrie': 9, 'Octombrie': 10, 'Noiembrie': 11, 'Decembrie': 12
        }
        parts = string_published_date.split()
        day = int(parts[0])
        month_str = parts[1]
        month = months.get(month_str, 1)
        current_year = datetime.datetime.now().year
        published_date = datetime.datetime(current_year, month, day)
        time_str = parts[-1]
        hours, minutes = map(int, time_str.split(':'))
        published_date = published_date.replace(hour=hours, minute=minutes)

        text_div = soup.find('div', class_='text')
        if text_div:
            p_elements = text_div.find_all('p')
            p_elements = p_elements[:-2] if p_elements else []
            article_text = []
            for p in p_elements:
                paragraph_text = p.get_text(strip=True)
                if paragraph_text:
                    normalized_text = unicodedata.normalize("NFKD", paragraph_text)
                    article_text.append(normalized_text)
            
        return {
            'author': author,
            'published_date': published_date,
            'tags': tags,
            'image_url': image_url,
            'article_text': article_text
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_antena3():
    conn = create_db_connection()
    cur = conn.cursor()
    source_name = 'Antena 3'
    custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": custom_user_agent}
    url = "https://www.antena3.ro/politica/pagina-1"
    stop_scraping = False
    latest_article_date = get_latest_article_date(source_name, cur)
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            lists = soup.find_all('ul', class_='cols1')
            for elements in lists:
                for element in elements:
                    element_article = element.find('article')
                    articles.append(element_article)

            for article in articles[:-1]:
                title = article.find('h2').find('a').get_text(strip=True)
                backup_image_element = article.find('div', class_='thumb')
                backup_image = backup_image_element.find('img')['data-src']
                article_url = article.find('h2').find('a')['href']
                article_data = scrape_article_antena3(article_url, title)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nAntena 3 - UPDATED.\n")
                            break

                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        content = f"{title} {article_data['article_text'][0]} {article_data['article_text'][1]}"
                        emotion_label = predict_label(content, tokenizer, model)

                        cur.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                        source_id_result = cur.fetchone()
                        source_id = source_id_result[0]

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source, emotion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            source_id,
                            emotion_label
                        ))
                        conn.commit()

                        cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
                        article_id = cur.fetchone()[0]

                        for paragraph_text in article_data['article_text']:
                            cur.execute("""
                                INSERT INTO article_paragraphs (article_id, paragraph_text)
                                VALUES (%s, %s)
                            """, (article_id, paragraph_text))
                            conn.commit()

                        match_tags_to_entities(article_data['tags'], article_id, published_date, cur, conn)

                        print(f"{source_name} INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)

            url = get_next_page_url_antena3(url)
            if url is None:
                stop_scraping = True
            # print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)

    cur.close()
    conn.close()
   
# source_scrapers = [scrape_hotnews]
source_scrapers = [scrape_ziaredotcom, scrape_adevarul, scrape_stiripesurse, scrape_digi24, 
                   scrape_protv, scrape_observator,  scrape_gandul, scrape_bursa, scrape_antena3, scrape_hotnews]

# mediafax iar are probleme cu get_text la date
#scrape_mediafax() # - are o problema la schimbarea paginii + aparent are problema ca la un moment dat zice ca date
# element e None....


