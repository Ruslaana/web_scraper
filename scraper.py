import requests
from bs4 import BeautifulSoup
import json
import os

sources = [
    "dr.dk",
    "nyheder.tv2.dk",
    "politiken.dk",
    "berlingske.dk",
    "jyllands-posten.dk",
    "information.dk",
    "altinget.dk",
    "borsen.dk",
    "kristeligt-dagblad.dk"
]

output_folder = "news_data"
os.makedirs(output_folder, exist_ok=True)

def download_image(image_url, output_folder, title):
    """Download and save the image locally."""
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_filename = f"{output_folder}/{title}.jpg"
            with open(image_filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return image_filename
    except Exception:
        pass
    return None

def scrape_news(source, output_folder):
    """Scrapes news from the given source."""
    url = f"https://{source}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text.strip() if soup.find("title") else "Untitled"
        date = soup.find("time").text.strip() if soup.find("time") else "Unknown date"

        paragraphs = soup.find_all("p")
        content = " ".join([p.text.strip() for p in paragraphs]) if paragraphs else "No content available"

        source_links = [a["href"] for a in soup.find_all("a", href=True)]

        image_url = soup.find("img")["src"] if soup.find("img") else None
        image_path = download_image(image_url, output_folder, title) if image_url else None

        return {
            "version": "1.0",
            "document": {
                "id": source.replace(".", "_"),
                "title": title,
                "content": {
                    "full_text": content
                },
                "metadata": {
                    "source": source,
                    "url": url,
                    "date": date,
                    "security_level": "public",
                    "image_url": image_url,
                    "image_path": image_path,
                    "source_links": source_links,
                    "attachments": []
                }
            }
        }
    else:
        print(f"❌ Error {response.status_code} while scraping {source}")
        return None

def save_news_file(news_data, output_folder):
    """Saves news data to a separate JSON file."""
    title_cleaned = "".join(c if c.isalnum() else "_" for c in news_data["document"]["title"])
    filename = f"{output_folder}/{title_cleaned}.json"

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(news_data, file, ensure_ascii=False, indent=4)
    
    print(f"✅ News saved: {filename}")

for source in sources:
    news_data = scrape_news(source, output_folder)
    if news_data:
        save_news_file(news_data, output_folder)
