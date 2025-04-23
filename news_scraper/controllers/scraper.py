import requests
from bs4 import BeautifulSoup
from controllers.image_handler import download_image
from models.news_model import NewsModel

def clean_title(title):
    return "".join([c for c in title if c not in r'\/:*?"<>|']).strip()

def validate_date(raw_date):
    return raw_date if raw_date else "No date available"

def scrape_news(source, output_folder):
    if not source.startswith("http"):
        url = f"https://{source}"
    else:
        url = source

    try:
        response = requests.get(url)
    except Exception as e:
        print(f"❌ Не вдалося отримати дані з URL {url}. Помилка: {e}")
        return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("title")
        raw_title = title_tag.text if title_tag else "Untitled"
        title = clean_title(raw_title)

        time_tag = soup.find("time")
        raw_date = time_tag.text if time_tag else None
        date = validate_date(raw_date)

        paragraphs = soup.find_all("p")
        content = " ".join([p.text.strip() for p in paragraphs]) if paragraphs else "No content available"

        img_tag = soup.find("img")
        image_url = img_tag["src"] if img_tag and img_tag.get("src") else None
        image_path = download_image(image_url, output_folder, title) if image_url else None

        meta_author = soup.find("meta", {"name": "author"})
        author = meta_author["content"] if meta_author and meta_author.get("content") else "Unknown author"

        related_links = [a["href"] for a in soup.find_all("a", href=True) if "content" in a["href"]]

        return NewsModel(source, title, content, date, image_url, image_path, author, related_links)
    else:
        print(f"❌ Error {response.status_code} while scraping {source}")
        return None
