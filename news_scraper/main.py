import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from scraper import scrape_news

def get_news_batch():
    sitemap_url = "https://www.berlingske.dk/sitemap.xml/tag/1"
    counter = 1
    news_batch = []

    response = requests.get(sitemap_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    loc_urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    news_urls = [url.text for url in loc_urls]

    print(f"🔍 Знайдено новин у sitemap: {len(news_urls)}")

    for news_url in news_urls:
        try:
            teaser_page = requests.get(news_url)
            soup = BeautifulSoup(teaser_page.text, 'lxml')
            teaser_link = soup.find('a', class_="teaser__title-link")

            if teaser_link and 'href' in teaser_link.attrs:
                full_url = "https://www.berlingske.dk" + teaser_link['href']
                news_data = scrape_news(full_url, counter)
                if news_data:
                    news_batch.append(news_data)
                    print(f"✅ Отримано новину ID {counter}")
                    counter += 1
        except Exception as e:
            print(f"❌ Помилка: {e}")

    return news_batch


if __name__ == "__main__":
    batch = get_news_batch()
    print(f"🔁 Отримано новин: {len(batch)}")