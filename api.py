import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from fastapi import FastAPI
from scraper.scraper import scrape_news

app = FastAPI()


@app.get("/latest")
def get_latest_news():
    try:
        sitemap_url = "https://www.berlingske.dk/sitemap.xml/tag/1"
        response = requests.get(sitemap_url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        loc_urls = root.findall(
            './/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        news_urls = [url.text for url in loc_urls]
        news_urls.reverse()

        for teaser_url in news_urls:
            teaser_page = requests.get(teaser_url)
            soup = BeautifulSoup(teaser_page.text, 'lxml')
            teaser_link = soup.find('a', class_="teaser__title-link")

            if teaser_link and 'href' in teaser_link.attrs:
                full_url = "https://www.berlingske.dk" + teaser_link['href']
                news = scrape_news(full_url)
                if news and news.title and news.content.strip():
                    return news.to_dict()
        return {"error": "❌ Не вдалося знайти жодної валідної новини"}

    except Exception as e:
        return {"error": f"❌ Помилка: {str(e)}"}
