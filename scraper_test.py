# import json
# import requests
# import xml.etree.ElementTree as ET
# from bs4 import BeautifulSoup

# def scrape_news(url):
#     try:
#         response = requests.get(url)

#         soup = BeautifulSoup(response.text, 'lxml')

#         title_tag = soup.find('h2', class_='article-header__title')
#         title = title_tag.get_text(strip=True) if title_tag else None

#         image_tag = soup.find('img', class_='article-top-media__image')
#         image_url = image_tag['src'] if image_tag else None

#         content_tag = soup.find('article', id='articleBody')
#         paragraphs = content_tag.find_all('p') if content_tag else []
#         content = '\n'.join(p.get_text(strip=True) for p in paragraphs)

#         time_tag = soup.find('div', class_="article-byline__date")
#         publication_time = time_tag.get_text(strip=True) if time_tag else None

#         author_tag = soup.find('div', class_="article-byline__author-name")
#         author = author_tag.get_text(strip=True) if author_tag else None

#         return {
#             "title": title,
#             "content": content,
#             "image_url": image_url,
#             "publication_time": publication_time,
#             "author": author
#         }

#     except requests.RequestException as e:
#         print(f"Error fetching the URL: {e}")
#         return None

# url = "https://www.berlingske.dk/sitemap.xml/tag/1"
# response = requests.get(url)
# response.raise_for_status()

# root = ET.fromstring(response.content)
# urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')

# news_urls = [url.text for url in urls[:3]]

# news_data = []
# for news_url in news_urls:
#     news_info = scrape_news(news_url)
#     if news_info:
#         news_data.append(news_info)

# with open('news.json', 'w', encoding='utf-8') as f:
#     json.dump(news_data, f, ensure_ascii=False, indent=4)

# print(f"News are saved in news.json")


import json
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# counting the number of news
sitemap_url = "https://www.berlingske.dk/sitemap.xml/tag/1"

response = requests.get(sitemap_url)
response.raise_for_status()
root = ET.fromstring(response.content)
loc_urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')

print(f"Number of news: {len(loc_urls)}")


def scrape_news(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        title_tag = soup.find('h2', class_='article-header__title')
        title = title_tag.get_text(strip=True) if title_tag else None

        image_tag = soup.find('img', class_='article-top-media__image')
        image_url = image_tag['src'] if image_tag else None

        content_tag = soup.find('article', id='articleBody')
        paragraphs = content_tag.find_all('p') if content_tag else []
        content = '\n'.join(p.get_text(strip=True) for p in paragraphs)

        time_tag = soup.find('div', class_="article-byline__date")
        publication_time = time_tag.get_text(strip=True) if time_tag else None

        author_tag = soup.find('div', class_="article-byline__author-name")
        author = author_tag.get_text(strip=True) if author_tag else None

        return {
            "title": title,
            "content": content,
            "image_url": image_url,
            "publication_time": publication_time,
            "author": author
        }

    except requests.RequestException as e:
        print(f"Error fetching the news page: {e}")
        return None

sitemap_url = "https://www.berlingske.dk/sitemap.xml/tag/1"
response = requests.get(sitemap_url)
response.raise_for_status()

root = ET.fromstring(response.content)
loc_urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')

news_urls = [url.text for url in loc_urls[:3]]

news_data = []
for news_url in news_urls:
    try:
        news_page = requests.get(news_url)
        soup = BeautifulSoup(news_page.text, 'lxml')

        h4_tag = soup.find('h4', class_="teaser__title d-inline-block font-s4")
        if h4_tag:
            teaser_link = h4_tag.find('a', class_="teaser__title-link")
            if teaser_link and teaser_link['href'] == news_url: 
                news_info = scrape_news(news_url)
                if news_info:
                    news_data.append(news_info)

    except requests.RequestException as e:
        print(f"Error accessing the news page: {e}")

with open('news.json', 'w', encoding='utf-8') as f:
    json.dump(news_data, f, ensure_ascii=False, indent=4)

print("News are saved in news.json")