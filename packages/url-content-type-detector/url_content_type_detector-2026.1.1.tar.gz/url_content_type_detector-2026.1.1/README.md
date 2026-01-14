# URL Content Type Detector

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org)

A lightweight, efficient utility to determine the content type of any URL with minimal overhead.

[Quick Start](#installation) • [Documentation](#usage) • [Examples](#examples) • [Contributing](#contributing)

</div>

---

## Overview

**URL Content Type Detector** is a Python library that retrieves the content type of a URL by making efficient HTTP HEAD requests. It's designed to be lightweight, robust, and production-ready with comprehensive error handling.

### Key Features

- 🚀 **Fast & Efficient**: Uses HTTP HEAD requests to minimize bandwidth
- ✅ **Robust Error Handling**: Custom exceptions and detailed error messages
- 🔒 **URL Validation**: Built-in URL validation using industry-standard validators
- ⏱️ **Configurable Timeout**: Adjustable timeout settings with sensible defaults
- 🛡️ **Security-First**: Optional strict HTTP status code validation
- 📦 **Lightweight**: Zero unnecessary dependencies beyond `requests` and `validators`
- 🧪 **Well-Tested**: Comprehensive test suite with pytest
- 🐍 **Python 3.14+**: Modern Python support

---

## Installation

### Using pip

```bash
pip install url-content-type-detector
```

### Using uv (recommended for development)

```bash
uv pip install url-content-type-detector
```

### Development Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/krsahil8825/url_content_type_detector.git
cd url_content_type_detector
uv pip install -e .
```

---

## Usage

### Basic Example

```python
from url_content_type_detector import get_content_type

# Get content type of a webpage
content_type = get_content_type("https://example.com")
print(content_type)  # Output: text/html; charset=UTF-8
```

### Detecting Different Content Types

```python
from url_content_type_detector import get_content_type

# HTML Page
html_type = get_content_type("https://example.com/page.html")
print(html_type)  # text/html; charset=UTF-8

# Image
image_type = get_content_type("https://example.com/image.png")
print(image_type)  # image/png

# PDF Document
pdf_type = get_content_type("https://example.com/document.pdf")
print(pdf_type)  # application/pdf

# JSON API
json_type = get_content_type("https://api.example.com/data")
print(json_type)  # application/json
```

### Advanced Configuration

```python
from url_content_type_detector import get_content_type, URLUtilsError

# Custom timeout (in seconds)
content_type = get_content_type("https://slow-server.com", timeout=30)

# Disable strict HTTP validation (allows 4xx/5xx responses)
try:
    content_type = get_content_type("https://example.com", is_secure=False)
except URLUtilsError as e:
    print(f"Error: {e}")

# No timeout (not recommended for production)
content_type = get_content_type("https://example.com", timeout=None)
```

---

## API Reference

### `get_content_type(url, timeout=10, is_secure=True)`

Fetches the content type of the resource at the given URL.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | Required | The URL of the resource |
| `timeout` | `int \| None` | `10` | Request timeout in seconds. Use `None` for no timeout (not recommended in production) |
| `is_secure` | `bool` | `True` | If `True`, raises an error for HTTP 4xx/5xx status codes |

**Returns:**

- `str`: The content type from the HTTP `Content-Type` header, or `"Not Found"` if missing

**Raises:**

- `ValueError`: If the URL is invalid or timeout is negative
- `URLUtilsError`: For network errors, timeouts, or (when `is_secure=True`) HTTP error responses
- `requests.RequestException`: For underlying request failures

**Example:**

```python
from url_content_type_detector import get_content_type, URLUtilsError

try:
    content_type = get_content_type("https://example.com", timeout=15)
    print(f"Content Type: {content_type}")
except ValueError as e:
    print(f"Invalid URL: {e}")
except URLUtilsError as e:
    print(f"Request failed: {e}")
```

### `URLUtilsError`

Custom exception for URL content type detection errors.

**Example:**

```python
from url_content_type_detector import URLUtilsError, get_content_type

try:
    content_type = get_content_type("https://example.com/nonexistent")
except URLUtilsError as e:
    print(f"URL Error: {e}")
```

---

## Examples

### Demo Script

Run the included demo to see the library in action:

```bash
python scripts/demo.py
```

**Output:**
```
✅ URL: https://www.example.com -> Content Type: text/html; charset=UTF-8
✅ URL: https://www.example.com/image.png -> Content Type: image/png
✅ URL: https://www.example.com/document.pdf -> Content Type: application/pdf
```

### Use Cases

#### 1. File Type Detection in Web Scrapers

```python
from url_content_type_detector import get_content_type

def should_download(url):
    """Check if URL points to an image."""
    try:
        content_type = get_content_type(url)
        return content_type.startswith("image/")
    except Exception:
        return False

urls = ["https://example.com/pic.jpg", "https://example.com/page.html"]
for url in urls:
    if should_download(url):
        print(f"Download {url}")
```

#### 2. Content-Based Routing

```python
from url_content_type_detector import get_content_type

def route_by_content(url):
    """Route processing based on content type."""
    try:
        content_type = get_content_type(url)
        if content_type.startswith("image/"):
            return "image_processor"
        elif content_type.startswith("video/"):
            return "video_processor"
        elif "json" in content_type:
            return "data_processor"
        else:
            return "generic_processor"
    except Exception:
        return "error_handler"
```

#### 3. Link Health Checking

```python
from url_content_type_detector import get_content_type, URLUtilsError

def check_link_health(url):
    """Check if a link is accessible and returns valid content."""
    try:
        content_type = get_content_type(url, is_secure=True)
        return {"url": url, "status": "OK", "content_type": content_type}
    except URLUtilsError as e:
        return {"url": url, "status": "ERROR", "error": str(e)}

links = ["https://example.com", "https://example.com/404"]
for link in links:
    print(check_link_health(link))
```

---

## Requirements

- **Python:** 3.14 or higher
- **requests:** >= 2.32.5
- **validators:** >= 0.35.0

---

## Performance Considerations

- **HTTP HEAD Requests**: The library uses HTTP HEAD requests instead of GET to minimize bandwidth usage
- **Timeout Defaults**: The default 10-second timeout is suitable for most use cases. Adjust based on your network conditions
- **Redirect Handling**: The library automatically follows HTTP redirects (up to 30 by default in requests)
- **Connection Pooling**: For bulk URL processing, consider using a `requests.Session` for connection reuse (future feature)

---

## Troubleshooting

### Common Issues

#### `ValueError: Invalid URL provided`
- Ensure the URL starts with `http://` or `https://`
- Check for typos or invalid characters
- URLs with spaces are automatically converted to `%20`

#### `URLUtilsError: The request timed out`
- Increase the `timeout` parameter
- Check your network connection
- Verify the server is responsive

#### `URLUtilsError: Accessing Unsecure URL`
- The server returned a 4xx or 5xx status code
- Set `is_secure=False` to allow error responses
- Verify the URL is correct and accessible

#### `URLUtilsError: Failed to fetch content type`
- Check your internet connection
- Verify the URL is accessible
- Some servers may block HEAD requests; check server configuration

---

## Contributing

Contributions are welcome! Here's how to get started:

### Setup Development Environment

```bash
git clone https://github.com/krsahil8825/url_content_type_detector.git
cd url_content_type_detector
uv pip install -e ".[dev]"
```

### Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Make Your Changes

- Write clear, commented code
- Add tests for new features
- Ensure all tests pass: `pytest`

### Submit a Pull Request

1. Push your branch to GitHub
2. Create a pull request with a clear description
3. Link any related issues

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions
- Keep functions focused and modular

---

## Roadmap

- [ ] Async support (`async_get_content_type`)
- [ ] Connection pooling for batch operations
- [ ] Caching layer for repeated URLs
- [ ] Support for custom headers
- [ ] Testing and build automation with GitHub Actions

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Author

**Kumar Sahil**
- GitHub: [@krsahil8825](https://github.com/krsahil8825)
- Email: krsahil8825@gmail.com
- Website: [krsahil.co.in](https://krsahil.co.in)

---

## Acknowledgments

- Built with [requests](https://requests.readthedocs.io/) for HTTP communication
- URL validation powered by [validators](https://validators.readthedocs.io/)
- Testing with [pytest](https://pytest.org/)

---

<div align="center">

**[⬆ back to top](#url-content-type-detector)**

Made with ❤️ by [Kumar Sahil](https://github.com/krsahil8825)

</div>
