import os
import json
from fastapi import FastAPI

app = FastAPI()
NEWS_FOLDER = "news_data"

@app.get("/latest")
def get_latest_news():
    try:
        files = [f for f in os.listdir(NEWS_FOLDER) if f.endswith(".json")]
        if not files:
            return {"error": "❌ Немає новин"}

        latest_file = max(
            files,
            key=lambda f: os.path.getmtime(os.path.join(NEWS_FOLDER, f))
        )
        latest_path = os.path.join(NEWS_FOLDER, latest_file)

        with open(latest_path, "r", encoding="utf-8") as file:
            news = json.load(file)
            return news

    except Exception as e:
        return {"error": f"❌ Сталася помилка: {e}"}
