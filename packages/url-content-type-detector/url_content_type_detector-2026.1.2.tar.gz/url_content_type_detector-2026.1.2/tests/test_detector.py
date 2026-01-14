"""
test_detector.py
~~~~~~~~~~~~~~~~

This module contains tests for the url_content_type_detector package.
"""
import pytest
import requests
from url_content_type_detector import get_content_type, URLUtilsError


class MockResponse:  # pylint: disable=too-few-public-methods
    """A mock response object for simulating requests responses."""

    def __init__(self, headers=None, status_code=200):
        self.headers = headers or {}
        self.status_code = status_code

    def raise_for_status(self):
        """Simulate raise_for_status behavior."""
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")


def test_detect_content_type_html(monkeypatch):
    """Test detection of HTML content type."""
    def mock_head(*_args, **_kwargs):
        return MockResponse(headers={"Content-Type": "text/html; charset=UTF-8"})

    monkeypatch.setattr(requests, "head", mock_head)

    content_type = get_content_type("https://example.com")
    assert content_type.startswith("text/html")


def test_detect_content_type_image(monkeypatch):
    """Test detection of image content type."""
    def mock_head(*_args, **_kwargs):
        return MockResponse(headers={"Content-Type": "image/webp"})

    monkeypatch.setattr(requests, "head", mock_head)

    content_type = get_content_type("https://example.com/image.webp")
    assert content_type == "image/webp"


def test_detect_content_type_pdf(monkeypatch):
    """Test detection of PDF content type."""
    def mock_head(*_args, **_kwargs):
        return MockResponse(headers={"Content-Type": "application/pdf"})

    monkeypatch.setattr(requests, "head", mock_head)

    content_type = get_content_type("https://example.com/file.pdf")
    assert content_type == "application/pdf"


def test_invalid_url():
    """Test handling of invalid URL."""
    with pytest.raises(ValueError):
        get_content_type("invalid_url")


def test_timeout_handling(monkeypatch):
    """Test handling of request timeout."""
    def mock_head(*_args, **_kwargs):
        raise requests.Timeout

    monkeypatch.setattr(requests, "head", mock_head)

    with pytest.raises(URLUtilsError):
        get_content_type("https://example.com", timeout=1)


def test_http_error(monkeypatch):
    """Test handling of HTTP error responses."""
    def mock_head(*_args, **_kwargs):
        return MockResponse(status_code=404)

    monkeypatch.setattr(requests, "head", mock_head)

    with pytest.raises(URLUtilsError):
        get_content_type("https://example.com", is_secure=True)


def test_redirect_handling(monkeypatch):
    """Test handling of URL redirects."""
    def mock_head(*_args, **_kwargs):
        return MockResponse(headers={"Content-Type": "text/html"})

    monkeypatch.setattr(requests, "head", mock_head)

    content_type = get_content_type("http://github.com")
    assert content_type == "text/html"


def test_query_params(monkeypatch):
    """Test handling of URLs with query parameters."""
    def mock_head(*_args, **_kwargs):
        return MockResponse(headers={"Content-Type": "image/png"})

    monkeypatch.setattr(requests, "head", mock_head)

    content_type = get_content_type("https://example.com/avatar.png?v=4")
    assert content_type == "image/png"
