import os
import json
import re
import requests
import schedule
import time
import logging
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from controllers.scraper import scrape_news
from dotenv import load_dotenv
import boto3
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:80]

def generate_news_id(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def news_exists(news_id):
    try:
        response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix="news/")
        if "Contents" not in response:
            return False
        for obj in response["Contents"]:
            if news_id in obj["Key"]:
                return True
        return False
    except Exception as e:
        logger.warning(f"⚠️ news_exists помилка: {e}")
        return False

def save_news_to_s3(news_data, news_url):
    try:
        title = news_data['document']['title']
        news_id = generate_news_id(news_url)
        slug = slugify(title)
        filename = f"{slug}-{news_id}.json"
        key = f"news/{filename}"

        s3.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=key,
            Body=json.dumps(news_data, ensure_ascii=False),
            ContentType='application/json'
        )
        logger.info(f"☁️ Збережено: {key}")
        return True

    except Exception as e:
        logger.error(f"❌ Помилка при збереженні: {e}")
        return False

def get_news_batch():
    sitemap_url = "https://www.berlingske.dk/sitemap.xml/tag/1"
    seen_titles = set()

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"❌ Помилка sitemap: {e}")
        return

    root = ET.fromstring(response.content)
    loc_urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    news_urls = [url.text for url in loc_urls]
    logger.info(f"🔍 Знайдено {len(news_urls)} новин у sitemap")

    news_urls.reverse()

    for i, news_url in enumerate(news_urls, 1):
        try:
            teaser_page = requests.get(news_url)
            soup = BeautifulSoup(teaser_page.text, 'lxml')
            teaser_link = soup.find('a', class_="teaser__title-link")

            if teaser_link and 'href' in teaser_link.attrs:
                full_url = "https://www.berlingske.dk" + teaser_link['href']
                news_id = generate_news_id(full_url)

                if news_exists(news_id):
                    logger.info(f"✅ Новина вже існує (зупинка): {news_id}")
                    break 

                news_data = scrape_news(full_url)
                if news_data and news_data.title and news_data.content.strip():
                    title = news_data.title.lower()
                    if title in seen_titles:
                        logger.info(f"🔁 Пропущено дублікат заголовка: {title[:60]}")
                        continue
                    seen_titles.add(title)
                    saved = save_news_to_s3(news_data.to_dict(news_id), full_url)
                    if saved and i % 100 == 0:
                        print(f"📦 Скраплено: {i} новин...")

        except Exception as e:
            logger.warning(f"⚠️ Помилка при обробці {news_url}: {e}")

if __name__ == "__main__":
    get_news_batch()
    schedule.every().hour.do(get_news_batch)
    logger.info("🚀 Скрепер запущено. Очікування за розкладом...")
    while True:
        schedule.run_pending()
        time.sleep(30)
