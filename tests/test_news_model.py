from news_scraper.models.news_model import NewsModel


def test_news_model_to_dict():
    model = NewsModel(
        source="https://example.com/news",
        title="Test Title",
        content="This is the content.",
        image_url="https://example.com/image.jpg",
        publication_time="2024-05-01",
        author="John Doe",
        related_links=["https://example.com/related"]
    )

    result = model.to_dict("123")

    assert result["version"] == "1.0"
    assert result["document"]["id"] == "123"
    assert result["document"]["title"] == "Test Title"
    assert result["document"]["content"] == "This is the content."

    metadata = result["document"]["metadata"]
    assert metadata["source"] == "https://example.com/news"
    assert metadata["image_url"] == "https://example.com/image.jpg"
    assert metadata["publication_time"] == "2024-05-01"
    assert metadata["author"] == "John Doe"
    assert metadata["related_links"] == ["https://example.com/related"]
    assert metadata["attachments"] == []
