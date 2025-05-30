import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from news_scraper.api import app

client = TestClient(app)


@patch("news_scraper.api.s3")
def test_get_latest_news(mock_s3):
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [
            {"Key": "news/1.json"},
            {"Key": "news/5.json"},
            {"Key": "news/3.json"},
        ]}
    ]
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps({"title": "Latest News"}).encode("utf-8"))
    }

    response = client.get("/latest")
    assert response.status_code == 200
    assert response.json()["title"] == "Latest News"


@patch("news_scraper.api.s3")
def test_get_random_news(mock_s3):
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [
            {"Key": "news/1.json"},
            {"Key": "news/2.json"},
        ]}
    ]
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps({"title": "Random News"}).encode("utf-8"))
    }

    response = client.get("/random")
    assert response.status_code == 200
    assert "title" in response.json()


@patch("news_scraper.api.s3")
def test_get_random_news_fallback(mock_s3):
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": []}
    ]

    response = client.get("/random")
    assert response.status_code == 200
    assert response.json()["fallback"] is True
