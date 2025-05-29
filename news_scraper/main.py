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

def get_latest_id():
    latest_id = 0
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=AWS_BUCKET_NAME, Prefix="news/"):
            for obj in page.get("Contents", []):
                match = re.search(r'news/(\d+)\.json$', obj["Key"])
                if match:
                    num = int(match.group(1))
                    latest_id = max(latest_id, num)
    except Exception as e:
        logger.warning(f"⚠️ Помилка при визначенні останнього ID: {e}")
    return latest_id

def get_existing_urls():
    urls = set()
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=AWS_BUCKET_NAME, Prefix="news/"):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if not key.endswith(".json"):
                    continue
                try:
                    response = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=key)
                    data = json.loads(response['Body'].read().decode('utf-8'))
                    source = data.get("document", {}).get("metadata", {}).get("source")
                    if source:
                        urls.add(source)
                except Exception as e:
                    logger.warning(f"⚠️ Неможливо прочитати {key}: {e}")
    except Exception as e:
        logger.error(f"❌ Помилка при зчитуванні існуючих URL: {e}")
    return urls

def save_news_to_s3(news_data, news_id):
    try:
        key = f"news/{str(news_id)}.json"
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

def get_news_batch(sitemap_url):
    seen_titles = set()
    current_id = get_latest_id()
    existing_urls = get_existing_urls()

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

                if full_url in existing_urls:
                    logger.info(f"🔁 Пропущено існуючу новину: {full_url}")
                    continue

                news_data = scrape_news(full_url)

                if news_data and news_data.title and news_data.content.strip():
                    title = news_data.title.lower()
                    if title in seen_titles:
                        logger.info(f"🔁 Пропущено дублікат заголовка: {title[:60]}")
                        continue
                    seen_titles.add(title)
                    existing_urls.add(full_url)

                    current_id += 1
                    saved = save_news_to_s3(news_data.to_dict(str(current_id)), current_id)

                    if saved and current_id % 100 == 0:
                        logger.info(f"📦 Скраплено: {current_id} новин...")

        except Exception as e:
            logger.warning(f"⚠️ Помилка при обробці {news_url}: {e}")

if __name__ == "__main__":
    get_news_batch("https://www.berlingske.dk/sitemap.xml/tag/1")
    schedule.every().hour.do(get_news_batch, "https://www.berlingske.dk/sitemap.xml/tag/1")
    logger.info("🚀 Скрепер запущено. Очікування за розкладом...")
    while True:
        schedule.run_pending()
        time.sleep(30)
