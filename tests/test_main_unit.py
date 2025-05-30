import json
import pytest
from unittest.mock import patch, MagicMock
from news_scraper.main import get_latest_id, get_existing_urls, save_news_to_s3


# get_latest_id
@patch("news_scraper.main.s3")
def test_get_latest_id(mock_s3):
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [
            {"Key": "news/3.json"},
            {"Key": "news/7.json"},
            {"Key": "news/1.json"},
        ]}
    ]
    result = get_latest_id()
    assert result == 7


# get_existing_urls – base case
@patch("news_scraper.main.s3")
def test_get_existing_urls(mock_s3):
    fake_body = MagicMock()
    fake_body.read.return_value = json.dumps({
        "document": {
            "metadata": {
                "source": "https://example.com/news-article"
            }
        }
    }).encode("utf-8")

    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": "news/1.json"}]}
    ]
    mock_s3.get_object.return_value = {"Body": fake_body}

    result = get_existing_urls()
    assert "https://example.com/news-article" in result
    assert isinstance(result, set)


# get_existing_urls – exception when reading an object
@patch("news_scraper.main.s3")
def test_get_existing_urls_object_exception(mock_s3):
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": "news/1.json"}]}
    ]
    mock_s3.get_object.side_effect = Exception("S3 read error")

    result = get_existing_urls()
    assert isinstance(result, set)
    assert len(result) == 0


# get_existing_urls – uncorrect JSON
@patch("news_scraper.main.s3")
def test_get_existing_urls_invalid_json(mock_s3):
    fake_body = MagicMock()
    fake_body.read.return_value = b'invalid json'

    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": "news/1.json"}]}
    ]
    mock_s3.get_object.return_value = {"Body": fake_body}

    result = get_existing_urls()
    assert isinstance(result, set)
    assert len(result) == 0


# save_news_to_s3 – success
@patch("news_scraper.main.s3")
def test_save_news_to_s3_success(mock_s3):
    mock_s3.put_object.return_value = True
    result = save_news_to_s3({"title": "Test"}, 5)
    assert result is True


# save_news_to_s3 – exception
@patch("news_scraper.main.s3")
def test_save_news_to_s3_failure(mock_s3):
    mock_s3.put_object.side_effect = Exception("S3 error")
    result = save_news_to_s3({"title": "Test"}, 99)
    assert result is False
