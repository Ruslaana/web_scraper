import requests
from bs4 import BeautifulSoup
from save_json import save_to_json

sources = [
    "https://www.dr.dk/nyheder",
    "https://nyheder.tv2.dk",
    "https://politiken.dk",
    "https://www.berlingske.dk",
    "https://jyllands-posten.dk",
    "https://www.information.dk",
    "https://www.altinget.dk",
    "https://borsen.dk",
    "https://www.kristeligt-dagblad.dk"
]

def scrape_news(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text.strip() if soup.find("title") else "No title found"
        paragraphs = soup.find_all("p")
        content = " ".join([p.text.strip() for p in paragraphs]) if paragraphs else "No content found"

        return {
            "version": "1.0",
            "document": {
                "id": url.split("/")[-1],
                "title": title,
                "content": {
                    "full_text": content
                },
                "metadata": {
                    "source": url,
                    "url": url,
                    "security_level": "public",
                    "attachments": []
                }
            }
        }
    else:
        print(f"❌ Error {response.status_code} while scraping {url}")
        return None

news_data = [scrape_news(source) for source in sources if scrape_news(source)]

save_to_json(news_data, filename="data.json")
