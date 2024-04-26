import re
import requests
import psycopg2
from bs4 import BeautifulSoup
import datetime

conn = psycopg2.connect(
    dbname="Licenta",
    user="postgres",
    password="password",
    host="localhost"
)
cur = conn.cursor()

def is_published_this_year(parsed_published_date):
    current_year = datetime.datetime.now().year
    return parsed_published_date.year == current_year

def parse_published_date_for_postgresql(published_date_str):
    months = {
        'Ianuarie': 'January', 'Februarie': 'February', 'Martie': 'March', 'Aprilie': 'April',
        'Mai': 'May', 'Iunie': 'June', 'Iulie': 'July', 'August': 'August',
        'Septembrie': 'September', 'Octombrie': 'October', 'Noiembrie': 'November', 'Decembrie': 'December'
    }

    parts = published_date_str.split(', ')
    if len(parts) >= 3:
        day_month_year = parts[1].split()
        time = parts[2].split()[1]
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

def get_next_page_mediafax(current_url):
    if '/page/' in current_url:
        url_parts = current_url.split('/')
        page_number = int(url_parts[-2])
        next_page_number = page_number + 1
        url_parts[-2] = str(next_page_number)
        next_page_url = '/'.join(url_parts)
    else:
        next_page_url = current_url.rstrip('/') + '/page/2/'

    return next_page_url

def get_next_page_protv(current_link):
    base_url = "https://stirileprotv.ro/stiri/politic/"
    if current_link == base_url:
        return base_url + "?page=2"
    elif "?page=" in current_link:
        current_page = int(current_link.split("=")[-1])
        next_page = current_page + 1
        return base_url + f"?page={next_page}"
    else:
        return None

def get_next_page_liberatea(url):
    return None

def get_latest_article_date(source):
    cur.execute("""
        SELECT MAX(published_date) FROM articles WHERE source = %s
    """, (source,))
    latest_date = cur.fetchone()[0]
    return latest_date

def scrape_article_ziaredotcom(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        author_div = soup.find('div', class_='news__author')
        author_name = author_div.span.get_text(strip=True)
        number_of_views = soup.find('div', class_='news__views').text.strip()
        img_tag = soup.find('a', class_='news__image').find('img')
        image_src = img_tag['src']
        content_div = soup.find('div', class_='news__content descriere_main article__marker')
        all_text = [p.get_text(strip=True) for p in content_div.find_all('p')]
        return {
            'url': article_url,
            'author': author_name,
            'number_of_views': number_of_views,
            'main_image_src': image_src,
            'article_text': all_text
        }
    else:
        print("Failed to scrape article:", article_url)

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
                    parsed_published_date = parse_published_date_for_postgresql(published_date)
                    parsed_published_date = datetime.datetime.strptime(parsed_published_date, '%Y-%m-%d %H:%M:%S')
                    if is_published_this_year(parsed_published_date):
                        if latest_article_date is not None and parsed_published_date <= latest_article_date:
                            stop_scraping = True
                            print("Ziare.com is UPDATED.")
                            break
                        article_url = link.a['href']
                        article_data = scrape_article_ziaredotcom(article_url)
                        if article_data:
                            article_text = '\n'.join(article_data['article_text'])
                            cur.execute("""
                                INSERT INTO articles (title, url, author, published_date, number_of_views, image_url, article_text, source)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                title,
                                article_data['url'],
                                article_data['author'],
                                parsed_published_date,
                                extract_number_from_string(article_data.get('number_of_views', 0)),
                                article_data.get('main_image_src', ''),
                                [article_text],
                                'ziaredotcom'
                            ))
                            conn.commit()
                        else:
                            print("Failed to scrape article:", article_url)
                    else:
                        stop_scraping = True
                        break
            url = get_next_page_ziaredotcom(soup)
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
            tags = ', '.join(tag.text.strip() for tag in tag_links)
        else:
            tags = "None"

        date_elements = soup.find('div', class_='author-meta')
        second_span_element = date_elements.find_all('span')[-1]
        published_date_text = second_span_element.text.strip()
        first_digit_index = next((i for i, c in enumerate(published_date_text) if c.isdigit()), None)
        published_date_str = published_date_text[first_digit_index:]
        published_date = datetime.datetime.strptime(published_date_str, '%d.%m.%Y %H:%M')

        content_div = soup.find('div', class_='entry data-app-meta data-app-meta-article')
        all_text = [p.get_text(strip=True) for p in content_div.find_all('p', attrs={'data-index': True})]
        all_text_as_string = '\n'.join(all_text)

        return {
            'author': author_name,
            'published_date': published_date,
            'tags': tags,
            'article_text': all_text_as_string
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_digi24():
    url = "https://www.digi24.ro/stiri/actualitate/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date("digi24")
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = soup.find_all('h2', class_='h4 article-title')
            for link in article_links:
                a_element = link.find('a')
                article_url = "https://www.digi24.ro" + link.a['href']
                title = a_element.get_text(strip=True)
                image_src = soup.find('img')['src']
                article_data = scrape_article_digi24(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nDigi24 is updated.\n")
                            break
                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, tags, image_url, article_text, source)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            article_data['published_date'],
                            article_data['tags'],
                            image_src,
                            article_data['article_text'],
                            "digi24"
                        ))
                        conn.commit()
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
            print("Failed to fetch page:", url)

def check_if_mediafax_is_updated(url):
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
            tags = ', '.join(dd.get_text(strip=True)[:-1] for dd in dd_elements)
        else:
            tags = "None"

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
        all_text = [p.get_text(strip=True) for p in content_div.find_all('p')]
        all_text_as_string = '\n'.join(all_text)

        return {
            'author': author_name,
            'published_date': published_date,
            'tags': tags,
            'number_of_views': number_of_views,
            'article_text': all_text_as_string
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_mediafax():
    base_url = "https://www.mediafax.ro/politic/arhiva/"
    current_date = datetime.datetime.now()
    current_month = current_date.month
    month_url = f"{base_url}2024/{current_month:02d}"
    print(month_url)
    if check_if_mediafax_is_updated(month_url):
        print("\nMediaFax is updated.\n")
    else:
        for month in range(current_month, 0, -1):
            month_url = f"{base_url}2024/{month:02d}"
            print(f"Scraping articles from: {month_url}")
            scrape_articles_from_month(month_url)

def scrape_articles_from_month(month_url):
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
                image_src = "https:" + soup.find('img')['src']
                article_data = scrape_article_mediafax(article_url)
                if article_data:
                    print(article_data['published_date'])
                    cur.execute("""
                        INSERT INTO articles (title, url, author, published_date, number_of_views, tags, image_url, article_text, source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        title,
                        article_url,
                        article_data['author'],
                        article_data['published_date'],
                        article_data['number_of_views'],
                        article_data['tags'],
                        image_src,
                        article_data['article_text'],
                        "mediafax"
                    ))
                    conn.commit()
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
            tags = ', '.join(tag_link.text for tag_link in tag_links)
        else:
            tags = "None"

        third_p = soup.find('div', class_='article--info').find_all('p')[2]
        date_string = third_p.get_text(strip=True).replace('Dată publicare:', '').strip()
        published_date = datetime.datetime.strptime(date_string, '%d-%m-%Y %H:%M')

        content_div = soup.find('div', class_='article--text')
        paragraphs = content_div.find_all('p')
        text = '\n'.join([p.get_text(strip=True) for p in paragraphs])

        return {
            'author': author_name,
            'published_date': published_date,
            'tags': tags,
            'article_text': text
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_protv():
    url = "https://stirileprotv.ro/stiri/politic/"
    stop_scraping = False
    latest_article_date = get_latest_article_date("protv")
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
                image_src = image_div.find('img')['data-src']

                article_data = scrape_article_protv(article_url)
                if article_data:
                    published_date = article_data['published_date']
                    print(published_date)
                    if is_published_this_year(published_date):
                        if latest_article_date is not None and published_date <= latest_article_date:
                            stop_scraping = True
                            print("\nProTV is updated.\n")
                            break
                        cur.execute("""
                            INSERT INTO articles (title, url, author, published_date, tags, image_url, article_text, source)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            title,
                            article_url,
                            article_data['author'],
                            article_data['published_date'],
                            article_data['tags'],
                            image_src,
                            article_data['article_text'],
                            "protv"
                        ))
                        conn.commit()
                        print("\nArticle INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", article_url)
            url = get_next_page_protv(url)
            if url is None:
                stop_scraping = True
        else:
            print("Failed to fetch page:", url)

def scrape_article_adevarul(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1', class_='titleAndHeadings svelte-hvtg27').text.strip()
        print(title)

        img_div = soup.find('div', class_='container-image  svelte-jd4qiv')
        img_element = img_div.find('img')
        image_src = img_element['src']

        author_span = soup.find('div', class_='authors metaFont svelte-hvtg27')
        if author_span:
            author_name = author_span.find('a').text.strip()
        else:
            author_name = "Unknown"
        print(author_name)

        tags_div = soup.find('div', class_='tags svelte-1kju2ho')
        if tags_div:
            a_tags = tags_div.find_all('a')
            tags_string = ', '.join(tag.get_text() for tag in a_tags)
        else:
            tags_string = "None"

        time_element = soup.find('time', class_='svelte-hvtg27')
        datetime_str = time_element['datetime']
        datetime_str_with_offset = datetime_str[:-1] + "+0000"
        published_date_long_format = datetime.datetime.strptime(datetime_str_with_offset, "%Y-%m-%dT%H:%M:%S.%f%z")
        string_published_date = published_date_long_format.strftime('%d-%m-%Y %H:%M')
        published_date = datetime.datetime.strptime(string_published_date, '%d-%m-%Y %H:%M')

        intro = soup.find('p', class_='intro').get_text(strip=True)
        content_wrapper = soup.find('div', id='content-wrapper')
        content_paragraphs = content_wrapper.find_all('p', class_=lambda x: x != 'btn-google-news')
        content = '\n'.join([paragraph.get_text(strip=True) for paragraph in content_paragraphs])
        text = intro + '\n' + content

        # a_element_comments_link = soup.find('a', class_='more mg-bottom-30')
        # if a_element_comments_link:
        #     comments_link = a_element_comments_link['href']
        #     print(comments_link)
        #     comments_text = extract_comments_from_link_libertatea(comments_link)
        # else:
        #     comments = []
        #     comments_text = ""
        #     comments_wrapper_div = soup.find('div', class_='comments-wrapper')
        #     comment_divs = comments_wrapper_div.find_all('div', class_='comment comment--subscriber')
        #     for div in comment_divs:
        #         second_paragraph = div.find_all('p')[1]
        #         comments.append(second_paragraph.get_text(strip=True))
        #     comments_text = '\n\n'.join(comments)

        return {
            'title': title,
            'author': author_name,
            'published_date': published_date,
            'tags': tags_string,
            'image_src': image_src,
            # 'comments_from_people': comments_text,
            'article_text': text
        }
    else:
        print("Failed to scrape article:", article_url)

def scrape_adevarul():
    url = "https://adevarul.ro/politica"
    stop_scraping = False
    latest_article_date = get_latest_article_date("adevarul_articles")
    print(latest_article_date)
    while not stop_scraping:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            first_part = soup.find('div', id='b-489c850e-0c7f-40e3-a26d-3094036072a2')
            rest_of_the_articles_div = soup.find('div', id='b-d3739cf7-fa12-475d-bccc-856eb0f20b50')
            first_part_links = first_part.find_all('a', class_='row summary svelte-1mo6hi5 small')
            rest_links = rest_of_the_articles_div.find_all('a', class_='row summary svelte-1mo6hi5 small')
            all_links = first_part_links + rest_links

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
                            INSERT INTO adevarul_articles (title, url, author, published_date, tags, main_image_src, comments_from_people, article_text)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            article_data['title'],
                            article_url,
                            article_data['author'],
                            article_data['published_date'],
                            article_data['tags'],
                            article_data['image_src'],
                            article_data['comments_from_people'],
                            article_data['article_text']
                        ))
                        conn.commit()
                        print("\nArticle INSERTED.\n")
                    else:
                        stop_scraping = True
                        break
                else:
                    print("Failed to scrape article:", url)
            url = get_next_page_liberatea(url)
            if url is None:
                stop_scraping = True
        else:
            print("Failed to fetch page:", url)




#scrape_ziaredotcom()
#scrape_digi24()
#scrape_mediafax() # - are o problema la schimbarea paginii
#scrape_protv()
#scrape_liberatatea() - au securitate capcha
#scrape_adevarul()
cur.close()
conn.close()



# def extract_comments_from_link_libertatea(comments_link):
#     comments = []
#     comments_text = ""
#     response = requests.get(comments_link)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         comments_wrapper_div = soup.find('div', class_='comments-wrapper')
#         comment_divs = comments_wrapper_div.find_all('div', class_='comment comment--subscriber')
#         for div in comment_divs:
#             second_paragraph = div.find_all('p')[1]
#             comments.append(second_paragraph.get_text(strip=True))
#
#         comments_text = '\n\n'.join(comments)
#
#     return comments_text
#
# def scrape_article_libertatea(article_url):
#     response = requests.get(article_url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         news_item_info_div = soup.find('div', class_='news-item-info')
#         signature_and_time_div = news_item_info_div.find('div', class_='signature-and-time')
#
#         title = news_item_info_div.find('h1').text.strip()
#         print(title)
#
#         img_element = soup.find('img', class_='img-responsive')
#         image_src = img_element['src']
#
#         author_span = signature_and_time_div.find('span', class_='authors')
#         if author_span:
#             author_name = author_span.get_text(strip=True)[3:]
#         else:
#             author_name = "Unknown"
#
#         tags_ul = soup.find('ul', id='tags')
#         if tags_ul:
#             tags = [tag.get_text(strip=True) for tag in tags_ul.find_all('a')]
#             tags_string = ', '.join(tags)
#         else:
#             tags_string = "None"
#
#         time_tag = signature_and_time_div.find('time', id='itemprop-datePublished')
#         datetime_str = time_tag['datetime']
#         published_date_long_format = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z")
#         string_published_date = published_date_long_format.strftime('%d-%m-%Y %H:%M')
#         published_date = datetime.datetime.strptime(string_published_date, '%d-%m-%Y %H:%M')
#
#         intro = soup.find('p', class_='intro').get_text(strip=True)
#         content_wrapper = soup.find('div', id='content-wrapper')
#         content_paragraphs = content_wrapper.find_all('p', class_=lambda x: x != 'btn-google-news')
#         content = '\n'.join([paragraph.get_text(strip=True) for paragraph in content_paragraphs])
#         text = intro + '\n' + content
#
#         a_element_comments_link = soup.find('a', class_='more mg-bottom-30')
#         if a_element_comments_link:
#             comments_link = a_element_comments_link['href']
#             print(comments_link)
#             comments_text = extract_comments_from_link_libertatea(comments_link)
#         else:
#             comments = []
#             comments_text = ""
#             comments_wrapper_div = soup.find('div', class_='comments-wrapper')
#             comment_divs = comments_wrapper_div.find_all('div', class_='comment comment--subscriber')
#             for div in comment_divs:
#                 second_paragraph = div.find_all('p')[1]
#                 comments.append(second_paragraph.get_text(strip=True))
#             comments_text = '\n\n'.join(comments)
#
#         return {
#             'title': title,
#             'author': author_name,
#             'published_date': published_date,
#             'tags': tags_string,
#             'image_src': image_src,
#             'comments_from_people': comments_text,
#             'article_text': text
#         }
#     else:
#         print("Failed to scrape article:", article_url)
#
# def scrape_liberatatea():
#     url = "https://www.libertatea.ro/politica"
#     stop_scraping = False
#     latest_article_date = get_latest_article_date("libertatea_articles")
#     print(latest_article_date)
#     while not stop_scraping:
#         response = requests.get(url)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')
#             sections = soup.find_all('section', class_='news-container')
#             for section in sections:
#                 urls_to_scrape = set()
#                 single_article_section = section.find('div', class_='news-item large ctg-news')
#                 if single_article_section:
#                     single_article_url = single_article_section.find('a')['href']
#                     urls_to_scrape.add(single_article_url)
#
#                 multiple_articles_section = section.find('ul', class_='small-news-wrapper')
#                 if multiple_articles_section:
#                     articles = multiple_articles_section.find_all('li')
#                     for article in articles:
#                         multiple_article_url = article.find('a')['href']
#                         urls_to_scrape.add(multiple_article_url)
#
#                 for article_url in urls_to_scrape:
#                     print(article_url)
#                     article_data = scrape_article_libertatea(article_url)
#                     if article_data:
#                         published_date = article_data['published_date']
#                         print("Published date str: ", published_date)
#                         if is_published_this_year(published_date):
#                             if latest_article_date is not None and published_date <= latest_article_date:
#                                 stop_scraping = True
#                                 print("\nLibertatea is updated.\n")
#                                 break
#                             cur.execute("""
#                                 INSERT INTO libertatea_articles (title, url, author, published_date, tags, main_image_src, comments_from_people, article_text)
#                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                             """, (
#                                 article_data['title'],
#                                 article_url,
#                                 article_data['author'],
#                                 article_data['published_date'],
#                                 article_data['tags'],
#                                 article_data['image_src'],
#                                 article_data['comments_from_people'],
#                                 article_data['article_text']
#                             ))
#                             conn.commit()
#                             print("\nArticle INSERTED.\n")
#                         else:
#                             stop_scraping = True
#                             break
#                     else:
#                         print("Failed to scrape article:", url)
#             url = get_next_page_liberatea(url)
#             if url is None:
#                 stop_scraping = True
#         else:
#             print("Failed to fetch page:", url)
