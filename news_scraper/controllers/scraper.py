import requests
from bs4 import BeautifulSoup
from controllers.image_handler import get_img_url
from models.news_model import NewsModel
from datetime import datetime

def clean_title(title):
    from bs4 import Tag
    if isinstance(title, Tag):
        return title.get_text(separator=" ").strip()
    return "".join([c for c in title if c not in r'\/:*?"<>|']).strip()

def detect_news_date(soup):
    time_span = soup.find("span", {"class": "ncpost-avatar-header__timestamp"})
    if time_span and time_span.text.strip():
        return time_span.text.strip()
    return datetime.now().strftime("%d-%m-%Y")

# def get_title(soup):
#     title_tag = soup.find("title")
#     if title_tag and title_tag.text.strip():
#         return clean_title(title_tag.text.strip())
#     
#     for tag in ["h1", "h2"]:
#         header_tag = soup.find(tag)
#         if header_tag and header_tag.text.strip():
#             return clean_title(header_tag.text.strip())
#     
#     for tag in ["div", "span"]:
#         candidate_tags = soup.find_all(tag)
#         for candidate in candidate_tags:
#             if candidate.text and len(candidate.text.strip()) > 20:
#                 return clean_title(candidate.text.strip())
#     
#     return "Untitled"

def get_title(soup):
    specific_title = soup.find("div", {
        "role": "heading",
        "id": "ncpost-list-post-title-9503254",
        "class": "ncpost-title"
    })
    if specific_title and specific_title.text.strip():
        return clean_title(specific_title.text.strip())

    title_tag = soup.find("title")
    if title_tag and title_tag.text.strip():
        return clean_title(title_tag.text.strip())

    for tag in ["h1", "h2"]:
        header_tag = soup.find(tag)
        if header_tag and header_tag.text.strip():
            return clean_title(header_tag.text.strip())

    for tag in ["div", "span"]:
        candidate_tags = soup.find_all(tag)
        for candidate in candidate_tags:
            if candidate.text and len(candidate.text.strip()) > 20:
                return clean_title(candidate.text.strip())

    return "Untitled"

def get_author(soup):
    author_tag = soup.find("div", {"class": "ncpost-avatar-header__name"})
    return author_tag.text.strip() if author_tag else "Unknown author"

def scrape_news(source, output_folder):
    url = source if source.startswith(("http://", "https://")) else f"https://{source}"
    
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"❌ Failed to retrieve data from URL {url}. Error: {e}")
        return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        raw_title = get_title(soup)
        title = clean_title(raw_title)

        date = detect_news_date(soup)

        paragraphs = soup.find_all("p")
        content = " ".join([p.text.strip() for p in paragraphs]) if paragraphs else "No content available"

        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            image_url = img_tag["src"]
            full_image_url = get_img_url(image_url, url)
        else:
            full_image_url = None

        author = get_author(soup)

        related_links = [a["href"] for a in soup.find_all("a", href=True) if "content" in a["href"]]

        return NewsModel(source, title, content, date, full_image_url, author, related_links)
    else:
        print(f"❌ Error {response.status_code} while scraping {source}")
        return None
