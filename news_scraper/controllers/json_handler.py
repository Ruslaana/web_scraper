import json
import os

def save_to_json(news_data, output_folder):
    news_dict = news_data.to_dict()
    title = news_dict["document"]["title"]

    sanitized_title = "_".join(title.split()).strip()

    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.join(output_folder, f"{sanitized_title}.json")
    
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(news_dict, file, ensure_ascii=False, indent=4)
        print(f"✅ News saved: {filename}")
    except Exception as e:
        print(f"❌ Failed to save JSON. Error: {e}")
