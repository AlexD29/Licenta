import random
import re
import string
import unicodedata
import requests
import psycopg2
from bs4 import BeautifulSoup
import datetime
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

conn = psycopg2.connect(
    dbname="Licenta",
    user="postgres",
    password="password",
    host="localhost"
)
cur = conn.cursor()

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

def get_latest_article_date(source):
    cur.execute("""
        SELECT MAX(published_date) FROM articles WHERE source = %s
    """, (source,))
    latest_date = cur.fetchone()[0]
    return latest_date

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
    if current_page_url[-1].isdigit():
        current_page_number = int(current_page_url.split('/')[-1])
        next_page_number = current_page_number + 1
        next_page_url = current_page_url.rsplit('/', 1)[0] + '/' + str(next_page_number)
    else:
        next_page_url = current_page_url + '/2'
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

def filter_and_normalize_tag(tag):
    tag = tag.lower()
    tag = tag.translate(str.maketrans('ăâîșț', 'aaist'))
    tag = unicodedata.normalize('NFKD', tag).encode('ASCII', 'ignore').decode('utf-8')
    return tag

def match_tags_to_entities(tags, article_id):
    unmatched_tags = []
    for tag in tags:
        entity_id = None
        tag_words = tag.split()
        for word in tag_words:
            entity_id, table_name = match_word_to_entities(word)
            if entity_id:
                insert_tag_and_entity(tag, entity_id, table_name, article_id)
                break
        if not entity_id:
            unmatched_tags.append(tag)
    
    if unmatched_tags:
        insert_unmatched_tags(unmatched_tags, article_id)

def match_word_to_entities(word):
    cur.execute("SELECT id FROM politicians WHERE LOWER(last_name) LIKE %s", ('%' + word.lower() + '%',))
    politician_id = cur.fetchone()
    if politician_id:
        return politician_id[0], 'politicians'
    
    cur.execute("SELECT id FROM cities WHERE LOWER(name) LIKE %s", ('%' + word.lower() + '%',))
    city_id = cur.fetchone()
    if city_id:
        return city_id[0], 'cities'

    cur.execute("SELECT id FROM political_parties WHERE LOWER(abbreviation) LIKE %s", ('%' + word.lower() + '%',))
    political_party_id = cur.fetchone()
    if political_party_id:
        return political_party_id[0], 'political_parties'
    
    return None, None

def insert_tag_and_entity(tag, entity_id, table_name, article_id):
    cur.execute("""
        INSERT INTO tags (article_id, tag_text)
        VALUES (%s, %s)
        RETURNING id
    """, (article_id, tag))
    tag_id = cur.fetchone()[0]
    
    if table_name == "politicians":
        cur.execute("""
            INSERT INTO tag_politician (tag_id, politician_id)
            VALUES (%s, %s)
        """, (tag_id, entity_id))
        conn.commit()
    elif table_name == "cities":
        cur.execute("""
            INSERT INTO tag_city (tag_id, city_id)
            VALUES (%s, %s)
        """, (tag_id, entity_id))
        conn.commit()
    elif table_name == "political_parties":
        cur.execute("""
            INSERT INTO tag_political_parties (tag_id, political_party_id)
            VALUES (%s, %s)
        """, (tag_id, entity_id))
        conn.commit()

def insert_unmatched_tags(unmatched_tags, article_id):
    for tag_text in unmatched_tags:
        cur.execute("""
            INSERT INTO tags (article_id, tag_text)
            VALUES (%s, %s)
        """, (article_id, tag_text))
        conn.commit()

def extract_article_id_ziaredotcom(article_url):
    segments = article_url.split('/')
    last_segment = segments[-1]
    match = re.search(r'\d+$', last_segment)
    if match:
        article_id = match.group(0)
        return article_id
    else:
        return None

def scrape_article_ziaredotcom(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        author_div = soup.find('div', class_='news__author')
        author_name = author_div.span.get_text(strip=True)

        number_of_views = soup.find('div', class_='news__views').text.strip()

        tags_div = soup.find('div', class_='tags__container article__marker')
        if tags_div:
            tags = [filter_and_normalize_tag(tag.get_text(strip=True)) for tag in tags_div.find_all('a')]
        else:
            tags = []

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
    url = "https://ziare.com/politica/stiri-politice/stiri/"
    stop_scraping = False
    latest_article_date = get_latest_article_date("ziaredotcom")
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
                            print("Ziare.com is UPDATED.")
                            break
                        article_url = link.a['href']
                        article_data = scrape_article_ziaredotcom(article_url)
                        if article_data:
                            cur.execute("""
                                INSERT INTO articles (title, url, author, published_date, number_of_views, image_url, source)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                title,
                                article_data['url'],
                                article_data['author'],
                                parsed_published_date,
                                extract_number_from_string(article_data.get('number_of_views', 0)),
                                article_data['image_url'],
                                'Ziare.com'
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

                            match_tags_to_entities(article_data['tags'], article_id)
                            
                            for comment_text in article_data['comments']:
                                cur.execute("""
                                    INSERT INTO comments (article_id, comment_text)
                                    VALUES (%s, %s)
                                """, (article_id, comment_text))
                                conn.commit()
                            print("Article INSERTED.\n")
                        else:
                            print("Failed to scrape article:", article_url)
                    else:
                        stop_scraping = True
                        break
            url = get_next_page_ziaredotcom(soup)
            if url is None:
                stop_scraping = True
            else:
                print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

def extract_author_name(link):
    author_name = link.replace('/autor/', '')
    author_name = author_name.replace('-', ' ').title()
    return author_name

def scrape_article_digi24(article_url):
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

        tag_elements = soup.find('ul', class_='tags-list')
        if tag_elements:
            tag_links = tag_elements.find_all('a')
            tags = [filter_and_normalize_tag(tag.get_text(strip=True)) for tag in tag_links]
        else:
            tags = []

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
    url = "https://www.digi24.ro/stiri/actualitate/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date("Digi24")
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
                article_data = scrape_article_digi24(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nDigi24 is updated.\n")
                            break
                        
                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            article_data['published_date'],
                            article_data['image_url'],
                            "Digi24"
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
                        
                        match_tags_to_entities(article_data['tags'], article_id)
                        
                        print("\nArticle INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_digi24(soup)
            if url is None:
                stop_scraping = True
            else:
                print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

def check_if_updated_mediafax(url):
    latest_article_date = get_latest_article_date("mediafax")
    print(latest_article_date)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_list = soup.find('ul', class_='intros')
        article_links = article_list.select(
            'a.title:not([title="UPDATE"]):not([title="LIVE TEXT"]):not([title="VIDEO"]):not([title="BREAKING NEWS"])')
        for link in article_links:
            article_url = link['href']
            article_data = scrape_article_mediafax(article_url)
            if article_data:
                published_date = article_data['published_date']
                if latest_article_date is not None and published_date <= latest_article_date:
                    print(published_date)
                    return True
    return False

def scrape_article_mediafax(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        a_element = soup.find('a', class_='author_link')
        if a_element:
            author_name = a_element.text.strip()
        else:
            author_name = "Unknown"

        dl_element = soup.find('dl', class_='a-tags')
        if dl_element:
            dd_elements = dl_element.find_all('dd')
            tags = [filter_and_normalize_tag(dd.get_text(strip=True))  for dd in dd_elements]
        else:
            tags = []

        print(tags)

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
        image_url_with_dimensions = image_div.find('img')['data-src']
        image_url = remove_image_dimensions(image_url_with_dimensions)

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
    base_url = "https://www.mediafax.ro/politic/arhiva/"
    current_date = datetime.datetime.now()
    current_month = current_date.month
    month_url = f"{base_url}2024/{current_month:02d}"
    print(month_url)
    if check_if_updated_mediafax(month_url):
        print("\nMediaFax is updated.\n")
    else:
        for month in range(current_month, 0, -1):
            month_url = f"{base_url}2024/{month:02d}"
            print(f"Scraping articles from: {month_url}")
            scrape_articles_from_month_mediafax(month_url)

def scrape_articles_from_month_mediafax(month_url):
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
                print(title)
                article_data = scrape_article_mediafax(article_url)
                if article_data:
                    cur.execute("""
                        INSERT INTO articles (title, url, author, number_of_views, published_date, image_url, source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        title,
                        article_url,
                        article_data['author'],
                        article_data['number_of_views'],
                        article_data['published_date'],
                        article_data['image_url'],
                        'Mediafax'
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

                    match_tags_to_entities(article_data['tags'], article_id)

                    print("\nArticle INSERTED.\n")
                else:
                    print("Failed to scrape article:", article_url)
            month_url = get_next_page_mediafax(month_url)
            print("\nPAGE CHANGED.\n", month_url)
            if month_url is None:
                stop_scraping = True
        else:
            print("Failed to fetch page:", month_url)

def scrape_article_protv(article_url):
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

        second_p = soup.find('div', class_='article--info').find_all('p')[1]
        if second_p:
            tag_links = second_p.find_all('a')
            tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            tags = []

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
    url = "https://stirileprotv.ro/stiri/politic/"
    stop_scraping = False
    latest_article_date = get_latest_article_date("PROTV")
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

                article_data = scrape_article_protv(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nPROTV is updated.\n")
                            break
                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            'PROTV'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        print("Article INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_protv(url)
            if url is None:
                stop_scraping = True
            else:
                print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

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

        tags_div = soup.find('div', class_='tags svelte-1kju2ho')
        if tags_div:
            a_tags = tags_div.find_all('a')
            tags_string = [filter_and_normalize_tag(tag.get_text()) for tag in a_tags]
        else:
            tags_string = []

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
            'tags': tags_string,
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
    url = "https://adevarul.ro/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date("Adevarul")
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
                    print(published_date)
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nAdevarul is updated.\n")
                            break
                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url['href'],
                            article_data['author'],
                            published_date,
                            article_data['image_url'],
                            'Adevarul'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        for comment_text in article_data['comments']:
                            cur.execute("""
                                INSERT INTO comments (article_id, comment_text)
                                VALUES (%s, %s)
                            """, (article_id, comment_text))
                            conn.commit()
                        print("Article INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)
            url = get_next_page_adevarul(url)
            if url is None:
                stop_scraping = True
            print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)

def scrape_article_observator(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        author_span = soup.find('span', class_='headline-link')
        if author_span:
            author = author_span.get_text(strip=True)
        else:
            author = "Unknown"

        tags_div = soup.find('div', class_='taguri')
        if tags_div:
            tag_links = tags_div.find_all('a')
            tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            tags = []

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
    url = "https://observatornews.ro/politic/"
    stop_scraping = False
    latest_article_date = get_latest_article_date("Observator")
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
                article_data = scrape_article_observator(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nObservator is updated.\n")
                            break
                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            'Observator'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        print("Article INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_observator(url)
            if url is None:
                stop_scraping = True
            else:
                print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

def scrape_article_hotnews(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('article', class_='article-page')

        title = main_div.find('h1', class_='title').text.strip()
        unwanted_words = ["VIDEO"]
        for word in unwanted_words:
            title = title.replace(word, "").strip()

        img_div = main_div.find('img', class_='lead-img')
        image_url_with_dimensions = img_div['src']
        image_url = remove_image_dimensions(image_url_with_dimensions)

        author_span = main_div.find('span', class_='author')
        if author_span:
            author_name = author_span.find('a').text.strip()
        else:
            author_name = "Unknown"

        tags = []
        words = re.findall(r'\b\w+\b', title)
        i = 0
        while i < len(words):
            word = words[i]
            if len(word) >= 3 and (word.isupper() or word[0].isupper()):
                # Check if next words also start with an uppercase letter
                while i + 1 < len(words) and words[i + 1][0].isupper():
                    word += ' ' + words[i + 1]
                    i += 1
                tag = filter_and_normalize_tag(word)
                tags.append(tag)
            i += 1

        unparsed_published_date = main_div.find('span', class_='ora is-actualitate').text.strip()
        published_date = parse_published_date(unparsed_published_date)
        published_date = datetime.datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')

        main_element = main_div.find('div', class_='article-body is-actualitate')
        article_text = [p.get_text(strip=True) for p in main_element.find_all('p')]

        comments_div = soup.find('div', id='comments')
        comments = []
        if comments_div:
            comment_bodies = comments_div.find_all('div', class_='comment-body')
            if comment_bodies:
                for comment_body in comment_bodies:
                    comments.append(comment_body.get_text(strip=True))
            
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

def scrape_hotnews():
    url = "https://www.hotnews.ro/politic"
    stop_scraping = False
    latest_article_date = get_latest_article_date("HotNews")
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            first_article = soup.find('div', class_='snip poz-1').find('a')

            rest_div_elements = soup.find_all('div', class_='grid-2x3x1')
            links = []
            links.append(first_article['href'])
            for div_element in rest_div_elements:
                articles = div_element.find_all('article')
                for article in articles:
                    first_a = article.select_one('a')
                    if first_a:
                        article_url = first_a['href']
                        links.append(article_url)

            for article_url in links:
                article_data = scrape_article_hotnews(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nHotNews is updated.\n")
                            break
                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            article_data['image_url'],
                            'HotNews'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        for comment_text in article_data['comments']:
                            cur.execute("""
                                INSERT INTO comments (article_id, comment_text)
                                VALUES (%s, %s)
                            """, (article_id, comment_text))
                            conn.commit()
                        print("Article INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)
            url = get_next_page_hotnews(url)
            if url is None:
                stop_scraping = True
            print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)

def scrape_article_stiripesurse(article_url):
    custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": custom_user_agent}
    response = requests.get(article_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        unfiltered_title = soup.find('h1', class_='article-single-title').get_text(strip=True)
        words_to_filter = ["VIDEO", "Video"]
        title_words = unfiltered_title.split()
        filtered_words = [word for word in title_words if word not in words_to_filter]
        title = ' '.join(filtered_words)

        info_div = soup.find('div', class_='article-single-meta')
        if info_div:
            unfiltered_author = info_div.find('address').get_text(strip=True)
            author = unfiltered_author.split(',')[0].strip()
        else:
            author = "Unknown"

        published_date_str = info_div.find('time').get_text(strip=True)
        published_date = datetime.datetime.strptime(published_date_str, '%d/%m/%Y %H:%M')

        second_p = soup.find('div', class_='article-tags')
        if second_p:
            tag_links = second_p.find_all('a')
            tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            tags = []

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
    url = "https://www.stiripesurse.ro/politica/page/1"
    custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": custom_user_agent}
    stop_scraping = False
    latest_article_date = get_latest_article_date("Stiri pe surse")
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
                number_of_views = views_span.get_text(strip=True)

                article_data = scrape_article_stiripesurse(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nStiri pe surse is updated.\n")
                            break

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, number_of_views, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            number_of_views,
                            article_data['image_url'],
                            'Stiri pe surse'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        print("Article INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_stiripesurse_and_gandul(url)
            if url is None:
                stop_scraping = True
            else:
                print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

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

        tags_div = soup.find('div', class_='single__tags mg-bottom-20')
        if tags_div:
            tag_links = tags_div.find_all('a')
            tags = [filter_and_normalize_tag(tag.text.strip()) for tag in tag_links]
        else:
            tags = []

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
    url = "https://www.gandul.ro/politica/page/1"
    stop_scraping = False
    latest_article_date = get_latest_article_date("Gândul")
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
                            print("\nGândul is updated.\n")
                            break

                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            'Gândul'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        print("Article INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_stiripesurse_and_gandul(url)
            if url is None:
                stop_scraping = True
            else:
                print("PAGE CHANGED:", url)
        else:
            print("Failed to fetch page:", url)

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

        tags_div = soup.find('footer', class_='post-meta').find('p')
        if tags_div:
            a_tags = tags_div.find_all('a')
            tags_string = [filter_and_normalize_tag(tag.get_text()) for tag in a_tags]
        else:
            tags_string = []

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
            'tags': tags_string,
            'image_url': image_url,
            'comments': comments,
            'article_text': article_text
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_bursa():
    url = "https://www.bursa.ro/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date("Bursa")
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
                            print("\nBursa is updated.\n")
                            break

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            published_date,
                            article_data['image_url'],
                            'Bursa'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        for comment_text in article_data['comments']:
                            cur.execute("""
                                INSERT INTO comments (article_id, comment_text)
                                VALUES (%s, %s)
                            """, (article_id, comment_text))
                            conn.commit()
                        print("Article INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)

            buttons = soup.find_all('a', class_='btn btn-primary btn-lg')
            url = get_next_page_bursa(buttons)
            if url is None:
                stop_scraping = True
            print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)

def scrape_article_antena3(article_url):
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

        tags_div = soup.find('div', class_='tags')
        if tags_div:
            a_tags = tags_div.find_all('a')
            tags_string = [filter_and_normalize_tag(tag.get_text()) for tag in a_tags]
        else:
            tags_string = []

        string_published_date = info_spans[1].text.strip()
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
            'tags': tags_string,
            'image_url': image_url,
            'article_text': article_text
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_antena3():
    custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    headers = {"User-Agent": custom_user_agent}
    url = "https://www.antena3.ro/politica/pagina-1"
    stop_scraping = False
    latest_article_date = get_latest_article_date("Antena 3")
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
                article_data = scrape_article_antena3(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nAntena 3 is updated.\n")
                            break

                        article_image_url = article_data['image_url']
                        if article_image_url is None:
                            article_image_url = backup_image

                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, image_url, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            published_date,
                            article_image_url,
                            'Antena 3'
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

                        match_tags_to_entities(article_data['tags'], article_id)

                        print("ARTICLE INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)

            url = get_next_page_url_antena3(url)
            if url is None:
                stop_scraping = True
            print("PAGE CHANGED: ", url)
        else:
            print("Failed to fetch page:", url)


#scrape_ziaredotcom()
#scrape_digi24()
#scrape_mediafax() # - are o problema la schimbarea paginii + aparent are problema ca la un moment dat zice ca date
# element e None....
#scrape_protv()
#scrape_adevarul()
#scrape_observator()
#scrape_hotnews()
#scrape_stiripesurse()
#scrape_gandul()
#scrape_bursa()
#scrape_antena3()
cur.close()
conn.close()

