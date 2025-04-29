from controllers.scraper import scrape_news
from controllers.json_handler import save_to_json

sources = [
    "https://www.berlingske.dk/sitemap.xml/tag/1",
]

output_folder = "news_data"

for source in sources:
    news_data = scrape_news(source)
    if news_data:
        save_to_json(news_data, output_folder)
    else:
        print(f"Failed to scrape news from source: {source}")