import os
import json
import boto3
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

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

NEWS_FOLDER = "news_data"
LAST_SAVED_ID_KEY = "meta/last_saved_id.txt"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def upload_to_s3(file_path, s3_key):
    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, AWS_BUCKET_NAME, s3_key)
        logger.info(f"☁️ Uploaded: {s3_key}")


def save_last_saved_id(news_id):
    try:
        s3.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=LAST_SAVED_ID_KEY,
            Body=str(news_id).encode("utf-8"),
            ContentType="text/plain"
        )
        logger.info(f"💾 Saved last_saved_id: {news_id}")
    except ClientError as e:
        logger.error(f"❌ Failed to save last_saved_id: {e}")


def migrate_all():
    if not os.path.exists(NEWS_FOLDER):
        logger.error(f"❌ Folder not found: {NEWS_FOLDER}")
        return

    files = [
        f for f in os.listdir(NEWS_FOLDER)
        if f.endswith(".json") and os.path.isfile(os.path.join(NEWS_FOLDER, f))
    ]

    if not files:
        logger.warning("⚠️ No JSON files found.")
        return

    files.sort(key=lambda f: os.path.getmtime(os.path.join(NEWS_FOLDER, f)))

    for filename in files:
        file_path = os.path.join(NEWS_FOLDER, filename)
        s3_key = f"news/{filename}"
        upload_to_s3(file_path, s3_key)

    last_file = files[-1]
    with open(os.path.join(NEWS_FOLDER, last_file), "r", encoding="utf-8") as f:
        last_data = json.load(f)
        last_id = last_data["document"]["id"]
        save_last_saved_id(last_id)


if __name__ == "__main__":
    migrate_all()
    logger.info("Migration completed.")