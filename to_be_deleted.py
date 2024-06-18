import re
import unicodedata
import requests
from bs4 import BeautifulSoup
import datetime

def filter_and_normalize_tag(tag):
    tag = tag.lower()
    tag = tag.translate(str.maketrans('ăâîșț', 'aaist'))
    tag = unicodedata.normalize('NFKD', tag).encode('ASCII', 'ignore').decode('utf-8')
    return tag

def remove_image_dimensions(image_url):
    return re.sub(r'\b(w|h)=\d+\b', '', image_url)

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

def extract_number_from_string(text):
    numbers = re.findall(r'\d+', text)
    return ''.join(numbers)

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


results = scrape_article_mediafax("https://www.mediafax.ro/politic/klaus-iohannis-emotionanta-victoria-de-astazi-a-echipei-noastre-de-fotbal-felicitari-tricolorilor-22409426", "Klaus Iohannis: Emoţionantă victoria de astăzi a echipei noastre de fotbal, felicitări tricolorilor")
print(results)