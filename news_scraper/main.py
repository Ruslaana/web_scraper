from controllers.scraper import scrape_news
from controllers.json_handler import save_to_json

sources = [
    "berlingske.dk",
    "information.dk",
    "weekendavisen.dk",
    "borsen.dk",
    "https://cphpost.dk"
]

output_folder = "news_data"

for source in sources:
    news_data = scrape_news(source, output_folder)
    if news_data:
        save_to_json(news_data, output_folder)
