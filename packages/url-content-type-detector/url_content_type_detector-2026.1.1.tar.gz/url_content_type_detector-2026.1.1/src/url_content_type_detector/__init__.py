"""
URL Content Type Detector
~~~~~~~~~~~~~~~~~~~~~~~~~

A utility to determine the content type of a URL.

Basic usage:

    >>> from url_content_type_detector import get_content_type
    >>> url = "https://example.com/image.png"
    >>> content_type = get_content_type(url)
    >>> print(content_type)
    image/png

This module provides a function to fetch the content type of a given URL
by making an HTTP HEAD request.
It also defines a custom exception for handling URL-related errors.

Copyright (c) 2026 Kumar Sahil
Licensed under the MIT License.
"""

from importlib.metadata import version
from .detector import get_content_type
from .exceptions import URLUtilsError

__all__ = ["get_content_type", "URLUtilsError"]


__version__ = version("url-content-type-detector")
