import requests
from bs4 import BeautifulSoup
from scraper.news_model import NewsModel
import logging

logger = logging.getLogger(__name__)


def scrape_news(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        title_tag = soup.find('h2', class_='article-header__title')
        image_tag = soup.find('img', class_='article-top-media__image')
        content_tag = soup.find('article', id='articleBody')
        pub_time_tag = soup.find('div', class_="article-byline__date")
        author_tag = soup.find('p', class_="article-byline__author-name")

        title = title_tag.get_text(strip=True) if title_tag else ""
        image_url = image_tag['src'] if image_tag else None
        content = ' '.join(p.get_text(strip=True)
                           for p in content_tag.find_all('p')) if content_tag else ""
        pub_time = pub_time_tag.get_text(strip=True) if pub_time_tag else None
        author = author_tag.get_text(strip=True) if author_tag else url

        logger.info(f"📰 {title[:60]}... ({len(content)} символів)")
        return NewsModel(
            source=url,
            title=title,
            content=content,
            image_url=image_url,
            publication_time=pub_time,
            author=author,
            related_links=[]
        )

    except Exception as e:
        logger.error(f"❌ scrape_news помилка: {e}")
        return None
