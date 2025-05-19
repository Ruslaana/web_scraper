import requests
from bs4 import BeautifulSoup
from models.news_model import NewsModel

def scrape_news(url, numeric_id):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        title_tag = soup.find('h2', class_='article-header__title')
        title = title_tag.get_text(strip=True) if title_tag else "Без заголовка"

        image_tag = soup.find('img', class_='article-top-media__image')
        image_url = image_tag['src'] if image_tag else None

        content_tag = soup.find('article', id='articleBody')
        paragraphs = content_tag.find_all('p') if content_tag else []
        content = ' '.join(p.get_text(strip=True) for p in paragraphs)

        time_tag = soup.find('div', class_="article-byline__date")
        publication_time = time_tag.get_text(strip=True) if time_tag else None

        author_tag = soup.find('p', class_="article-byline__author-name")
        author = author_tag.get_text(strip=True) if author_tag else None

        return NewsModel(
            numeric_id,
            source=url,
            title=title,
            content=content,
            image_url=image_url,
            publication_time=publication_time,
            author=author,
            related_links=[]
        )
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return None