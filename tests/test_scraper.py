import pytest
from unittest.mock import patch, MagicMock
from news_scraper.controllers.scraper import scrape_news


@patch("news_scraper.controllers.scraper.requests.get")
def test_scrape_news_success(mock_get):
    html = """
        <html>
            <h2 class='article-header__title'>Test Title</h2>
            <img class='article-top-media__image' src='https://example.com/image.jpg'/>
            <article id='articleBody'>
                <p>Paragraph 1.</p>
                <p>Paragraph 2.</p>
            </article>
            <div class='article-byline__date'>2024-05-01</div>
            <p class='article-byline__author-name'>John Doe</p>
        </html>
    """
    mock_response = MagicMock()
    mock_response.text = html
    mock_get.return_value = mock_response

    result = scrape_news("https://example.com/news")

    assert result is not None
    assert result.title == "Test Title"
    assert result.image_url == "https://example.com/image.jpg"
    assert "Paragraph 1." in result.content
    assert result.publication_time == "2024-05-01"
    assert result.author == "John Doe"


@patch("news_scraper.controllers.scraper.requests.get")
def test_scrape_news_missing_fields(mock_get):
    html = """
        <html>
            <article id='articleBody'><p>Only content.</p></article>
        </html>
    """
    mock_response = MagicMock()
    mock_response.text = html
    mock_get.return_value = mock_response

    result = scrape_news("https://example.com/news")

    assert result.title == ""
    assert result.image_url is None
    assert "Only content." in result.content
    assert result.author == "https://example.com/news"


@patch("news_scraper.controllers.scraper.requests.get", side_effect=Exception("Connection error"))
def test_scrape_news_request_exception(mock_get):
    result = scrape_news("https://example.com/broken")
    assert result is None
