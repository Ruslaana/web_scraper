from unittest.mock import patch, MagicMock
from news_scraper.main import get_news_batch

#  Успішне виконання всього ланцюжка


@patch("news_scraper.main.requests.get")
@patch("news_scraper.main.scrape_news")
@patch("news_scraper.main.save_news_to_s3")
@patch("news_scraper.main.get_existing_urls")
@patch("news_scraper.main.get_latest_id")
def test_get_news_batch_full_flow(
    mock_get_latest_id,
    mock_get_existing_urls,
    mock_save,
    mock_scrape,
    mock_requests
):
    mock_get_latest_id.return_value = 100
    mock_get_existing_urls.return_value = set()

    sitemap_xml = """
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/news-teaser</loc></url>
    </urlset>
    """
    teaser_html = '<a class="teaser__title-link" href="/news/full-article"></a>'

    mock_requests.side_effect = [
        MagicMock(content=sitemap_xml.encode("utf-8"), status_code=200),
        MagicMock(text=teaser_html, status_code=200),
    ]

    mock_scrape.return_value = MagicMock(
        title="Integration Title",
        content="Some content",
        to_dict=lambda id: {
            "id": id,
            "title": "Integration Title",
            "content": "Some content"
        }
    )

    mock_save.return_value = True

    get_news_batch("https://dummy-sitemap.com")

    mock_scrape.assert_called_once_with(
        "https://www.berlingske.dk/news/full-article")
    mock_save.assert_called_once()


#  Edge-case: існуючий URL
@patch("news_scraper.main.requests.get")
@patch("news_scraper.main.scrape_news")
@patch("news_scraper.main.save_news_to_s3")
@patch("news_scraper.main.get_existing_urls")
@patch("news_scraper.main.get_latest_id")
def test_get_news_batch_skips_existing_url(
    mock_get_latest_id,
    mock_get_existing_urls,
    mock_save,
    mock_scrape,
    mock_requests
):
    mock_get_latest_id.return_value = 10
    mock_get_existing_urls.return_value = {
        "https://www.berlingske.dk/news/full-article"}

    sitemap_xml = """
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/news-teaser</loc></url>
    </urlset>
    """
    teaser_html = '<a class="teaser__title-link" href="/news/full-article"></a>'

    mock_requests.side_effect = [
        MagicMock(content=sitemap_xml.encode("utf-8"), status_code=200),
        MagicMock(text=teaser_html, status_code=200)
    ]

    mock_scrape.return_value = MagicMock(
        title="Already Exists",
        content="some content",
        to_dict=lambda id: {}
    )

    get_news_batch("https://dummy-sitemap.com")

    mock_save.assert_not_called()


# Виняток при HTTP-запиті до sitemap
@patch("news_scraper.main.requests.get", side_effect=Exception("HTTP error"))
def test_get_news_batch_sitemap_exception(mock_get):
    get_news_batch("https://fail.com")
    # Перевіряємо, що немає краху — просто return


# Невалідний XML → виняток при fromstring
@patch("news_scraper.main.requests.get")
def test_get_news_batch_invalid_xml(mock_get):
    mock_get.return_value = MagicMock(content=b'invalid xml', status_code=200)
    get_news_batch("https://dummy.com")
    # Має просто обробити помилку і return
