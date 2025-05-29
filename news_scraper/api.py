import os
import json
import random
import boto3
from fastapi import FastAPI
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import re

load_dotenv()

app = FastAPI()

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

def load_all_news_keys():
    keys = []
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=AWS_BUCKET_NAME, Prefix="news/"):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if re.match(r'news/\d+\.json$', key):
                    keys.append(key)
    except Exception:
        pass
    return keys

@app.get("/latest")
def get_latest_news():
    try:
        keys = load_all_news_keys()
        if not keys:
            return {"error": "❌ Немає новин у архіві"}

        latest_key = max(keys, key=lambda k: int(re.search(r'(\d+)\.json$', k).group(1)))
        obj = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=latest_key)
        return json.loads(obj["Body"].read().decode("utf-8"))

    except ClientError as ce:
        return {"error": f"AWS помилка: {str(ce)}"}
    except Exception as e:
        return {"error": f"❌ Помилка: {str(e)}"}

@app.get("/random")
def get_random_news():
    try:
        keys = load_all_news_keys()
        if not keys:
            return {"fallback": True, "message": "📭 Тимчасово не знайдено новин"}

        random_key = random.choice(keys)
        obj = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=random_key)
        return json.loads(obj["Body"].read().decode("utf-8"))

    except Exception as e:
        return {"error": f"❌ Помилка при читанні новини: {str(e)}"}
