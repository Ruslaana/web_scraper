import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from controllers.scraper import scrape_news
from controllers.json_handler import save_to_json

output_folder = "news_data"
sitemap_url = "https://www.berlingske.dk/sitemap.xml/tag/1"

response = requests.get(sitemap_url)
response.raise_for_status()
root = ET.fromstring(response.content)

loc_urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')

print(f"Number of news: {len(loc_urls)}")


news_urls = [url.text for url in loc_urls] 

for news_url in news_urls:
    try:
        teaser_page = requests.get(news_url)
        soup = BeautifulSoup(teaser_page.text, 'lxml')

        h4_tag = soup.find('h4', class_="teaser__title d-inline-block font-s4")
        if h4_tag:
            teaser_link = h4_tag.find('a', class_="teaser__title-link")
            if teaser_link and 'href' in teaser_link.attrs:
                full_news_url = "https://www.berlingske.dk" + teaser_link['href']

                news_data = scrape_news(full_news_url)
                if news_data:
                    save_to_json(news_data, output_folder)

    except requests.RequestException as e:
        print(f"❌ Error accessing teaser page: {e}")
