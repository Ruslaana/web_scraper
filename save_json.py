import json

def save_to_json(data, filename="data.json"):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"✅ Data successfully saved to {filename}")
    except Exception as e:
        print(f"❌ Error writing JSON: {e}")
