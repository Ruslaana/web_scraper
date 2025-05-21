import os
import json
import boto3
import random
from fastapi import FastAPI
from dotenv import load_dotenv
from botocore.exceptions import ClientError

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


@app.get("/latest")
def get_latest_news():
    try:
        response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix="news/")
        items = response.get("Contents", [])

        if not items:
            return {"error": "❌ Немає новин в архіві"}

        latest = max(items, key=lambda x: x["LastModified"])
        key = latest["Key"]

        obj = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=key)
        return json.loads(obj["Body"].read().decode("utf-8"))

    except ClientError as ce:
        return {"error": f"AWS помилка: {str(ce)}"}
    except Exception as e:
        return {"error": f"❌ Сталася помилка: {str(e)}"}


@app.get("/random")
def get_random_news():
    try:
        response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix="news/")
        items = response.get("Contents", [])

        if not items:
            return {"error": "❌ Архів новин порожній"}

        key = random.choice(items)["Key"]
        obj = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=key)
        return json.loads(obj["Body"].read().decode("utf-8"))

    except Exception as e:
        return {"error": f"❌ Помилка при читанні новини: {str(e)}"}
