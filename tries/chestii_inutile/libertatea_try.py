# import datetime
# from bs4 import BeautifulSoup
# import requests


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

#         comments_text = '\n\n'.join(comments)

#     return comments_text

# def scrape_article_libertatea(article_url):
#     response = requests.get(article_url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         news_item_info_div = soup.find('div', class_='news-item-info')
#         signature_and_time_div = news_item_info_div.find('div', class_='signature-and-time')

#         title = news_item_info_div.find('h1').text.strip()
#         print(title)

#         img_element = soup.find('img', class_='img-responsive')
#         image_src = img_element['src']

#         author_span = signature_and_time_div.find('span', class_='authors')
#         if author_span:
#             author_name = author_span.get_text(strip=True)[3:]
#         else:
#             author_name = "Unknown"

#         tags_ul = soup.find('ul', id='tags')
#         if tags_ul:
#             tags = [tag.get_text(strip=True) for tag in tags_ul.find_all('a')]
#             tags_string = ', '.join(tags)
#         else:
#             tags_string = "None"

#         time_tag = signature_and_time_div.find('time', id='itemprop-datePublished')
#         datetime_str = time_tag['datetime']
#         published_date_long_format = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z")
#         string_published_date = published_date_long_format.strftime('%d-%m-%Y %H:%M')
#         published_date = datetime.datetime.strptime(string_published_date, '%d-%m-%Y %H:%M')

#         intro = soup.find('p', class_='intro').get_text(strip=True)
#         content_wrapper = soup.find('div', id='content-wrapper')
#         content_paragraphs = content_wrapper.find_all('p', class_=lambda x: x != 'btn-google-news')
#         content = '\n'.join([paragraph.get_text(strip=True) for paragraph in content_paragraphs])
#         text = intro + '\n' + content

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

#                 multiple_articles_section = section.find('ul', class_='small-news-wrapper')
#                 if multiple_articles_section:
#                     articles = multiple_articles_section.find_all('li')
#                     for article in articles:
#                         multiple_article_url = article.find('a')['href']
#                         urls_to_scrape.add(multiple_article_url)

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









# def scrape_article_b1(article_url):
#     headers = {"User-Agent": get_random_user_agent()}
#     response = requests.get(article_url, headers=headers)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')

#         title = soup.find('h1', class_='font-titles').get_text(strip=True)

#         author_div = soup.find('div', class_='name')
#         if author_div:
#             author = author_div.find('a').get_text(strip=True)
#         else:
#             author = "Unknown"

#         date_time_str = soup.find('span', class_='date_published').get_text(strip=True)
#         months = {
#             'ianuarie': 'January', 'februarie': 'February', 'martie': 'March', 'aprilie': 'April',
#             'mai': 'May', 'iunie': 'June', 'iulie': 'July', 'august': 'August',
#             'septembrie': 'September', 'octombrie': 'October', 'noiembrie': 'November', 'decembrie': 'December'
#         }
#         for month_name_ro, month_name_en in months.items():
#             if month_name_ro in date_time_str:
#                 date_time_str = date_time_str.replace(month_name_ro, month_name_en)
#                 break
#         format_str = "%d %B %Y, %H:%M"
#         published_date = datetime.datetime.strptime(date_time_str, format_str)

#         tags_div = soup.find('div', class_='single__tags mg-bottom-20')
#         if tags_div:
#             tag_links = tags_div.find_all('a')
#             tags = [tag.text.strip() for tag in tag_links]
#         else:
#             tags = []

#         image_element = soup.find('div', class_='single__media').find('picture')
#         if image_element:
#             img_tag = image_element.find('img')
#             if img_tag:
#                 image_url = img_tag['src']
#             else:
#                 image_url = None
#         else:
#             image_url = None

#         single_content_div = soup.find('div', class_='single__content')
#         article_text = []
#         all_elements = single_content_div.find_all('p')
#         for element in all_elements:
#             if element.text.strip():
#                 normalized_text = unicodedata.normalize("NFKD", element.text.strip())
#                 article_text.append(normalized_text)
                    
#         return {
#             'title': title,
#             'author': author,
#             'published_date': published_date,
#             'tags': tags,
#             'article_text': article_text,
#             'image_url': image_url
#         }
#     else:
#         print("Failed to scrape article:", article_url)

# article = scrape_article_b1("https://www.b1tv.ro/politica/angel-tilvar-mapn-ne-vom-ruga-in-seara-sfanta-pentru-pacea-si-linistea-celor-aproape-700-de-militari-aflati-in-misiuni-departe-de-tara-1456337.html")
# print(article['image_url'])

# def scrape_b1():
#     headers = {"User-Agent": get_random_user_agent()}
#     url = "https://www.b1tv.ro/politica/page/1"
#     stop_scraping = False
#     latest_article_date = get_latest_article_date("B1")
#     print(latest_article_date)
#     while not stop_scraping:
#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')

#             articles = []
#             divs = soup.find_all('div', class_='article__content')
#             for div in divs:
#                 link = div.find('h2').find('a')['href']
#                 articles.append(link)

#             for article_url in articles:
#                 print(article_url)
#                 article_data = scrape_article_b1(article_url)
#                 if article_data:
#                     published_date = article_data['published_date']
#                     if is_published_this_year(published_date):
#                         if latest_article_date is not None and published_date <= latest_article_date:
#                             stop_scraping = True
#                             print("\nB1 is updated.\n")
#                             break

#                         cur.execute("""
#                             INSERT INTO articles (title, url, author, published_date, image_url, source)
#                             VALUES (%s, %s, %s, %s, %s, %s)
#                         """, (
#                             article_data['title'],
#                             article_url,
#                             article_data['author'],
#                             published_date,
#                             article_data['image_url'],
#                             'B1'
#                         ))
#                         conn.commit()

#                         cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
#                         article_id = cur.fetchone()[0]

#                         for paragraph_text in article_data['article_text']:
#                             cur.execute("""
#                                 INSERT INTO article_paragraphs (article_id, paragraph_text)
#                                 VALUES (%s, %s)
#                             """, (article_id, paragraph_text))
#                             conn.commit()

#                         for tag_text in article_data['tags']:
#                             cur.execute("""
#                                 INSERT INTO tags (article_id, tag_text)
#                                 VALUES (%s, %s)
#                             """, (article_id, tag_text))
#                             conn.commit()

#                         print("Article INSERTED.\n")
#                     else:
#                         stop_scraping = True
#                         break
#                 else:
#                     print("Failed to scrape article:", article_url)
#             url = get_next_page_stiripesurse_and_gandul(url)
#             if url is None:
#                 stop_scraping = True
#             else:
#                 print("PAGE CHANGED:", url)
#         else:
#             print("Failed to fetch page:", url)





# def scrape_article_agerpres(article_url):
#     custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
#     headers = {"User-Agent": custom_user_agent}
#     response = requests.get(article_url, headers=headers)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         info_div = soup.find('div', class_='owl-item cloned')
#         print(info_div)
#         title = info_div.find('div', class_='details_news').find('h2').get_text(strip=True)

#         image_element = info_div.find('div', id='img_wrapper p_r').find('img')
#         if image_element:
#             image_url = "https://www.agerpres.ro" + image_element['src']
#         else:
#             image_url = None

#         author = "Unknown"

#         published_date_str = info_div.find('time', class_='timeago').get_text(strip=True)
#         published_date = datetime.strptime(published_date_str, '%Y-%m-%d %H:%M:%S')

#         p_element = soup.find('div', class_='description_articol').find('p')
#         article_text = [unicodedata.normalize("NFKD", paragraph.strip()) for paragraph in p_element.stripped_strings]
            
#         return {
#             'title': title,
#             'author': author,
#             'published_date': published_date,
#             'image_url': image_url,
#             'article_text': article_text
#         }
#     else:
#         print("Failed to scrape article:", article_url)

# # article = scrape_article_agerpres("https://www.agerpres.ro/politica/2024/05/03/kavalec-jurnalistii-joaca-un-rol-cheie-in-asigurarea-responsabilitatii-guvernelor-si-a-institutiilor-si-in-a-furniza-cetatenilor-informatii-esentiale--1290153")
# # print(article)

# def scrape_agerpres():
#     custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
#     headers = {"User-Agent": custom_user_agent}
#     url = "https://www.agerpres.ro/politica/page/1"
#     stop_scraping = False
#     latest_article_date = get_latest_article_date("Agerpres")
#     print(latest_article_date)
#     while not stop_scraping:
#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')

#             articles = []
#             if url == "https://www.agerpres.ro/politica/page/1":
#                 article_tag = soup.find('article', class_='main_news')
#                 onclick_value = article_tag.get('onclick')
#                 if onclick_value:
#                     link = "https://www.agerpres.ro/" + onclick_value.split("'")[1]
#                     articles.append(link)

#             articles_elements = soup.find_all('article', class_='unit_news shadow p_r')
#             for article_element in articles_elements:
#                 link = "https://www.agerpres.ro/" + article_element.find('div', class_='title_news').find('h2').find('a')['href']
#                 articles.append(link)

#             for article_url in articles:
#                 # title = article.find('h2').find('a').get_text(strip=True)
#                 # backup_image_element = article.find('div', class_='thumb')
#                 # backup_image = backup_image_element.find('img')['data-src']
#                 # article_url = article.find('h2').find('a')['href']
#                 article_data = scrape_article_antena3(article_url)
#                 if article_data:
#                     published_date = article_data['published_date']
#                     if is_published_this_year(published_date):
#                         if latest_article_date is not None and published_date <= latest_article_date:
#                             stop_scraping = True
#                             print("\nAgerpres is updated.\n")
#                             break

#                         # article_image_url = article_data['image_url']
#                         # if article_image_url is None:
#                         #     article_image_url = backup_image

#                         cur.execute("""
#                             INSERT INTO articles (title, url, author, published_date, image_url, source)
#                             VALUES (%s, %s, %s, %s, %s, %s)
#                         """, (
#                             article_data['title'],
#                             article_url,
#                             article_data['author'],
#                             published_date,
#                             article_data['image_url'],
#                             'Agerpres'
#                         ))
#                         conn.commit()

#                         cur.execute("SELECT id FROM articles WHERE url = %s", (article_url,))
#                         article_id = cur.fetchone()[0]

#                         for paragraph_text in article_data['article_text']:
#                             cur.execute("""
#                                 INSERT INTO article_paragraphs (article_id, paragraph_text)
#                                 VALUES (%s, %s)
#                             """, (article_id, paragraph_text))
#                             conn.commit()

#                         print("ARTICLE INSERTED.\n")
#                     else:
#                         stop_scraping = True
#                         break
#                 else:
#                     print("Failed to scrape article:", url)

#             url = get_next_page_url_antena3(url)
#             if url is None:
#                 stop_scraping = True
#             print("PAGE CHANGED: ", url)
#         else:
#             print("Failed to fetch page:", url)
