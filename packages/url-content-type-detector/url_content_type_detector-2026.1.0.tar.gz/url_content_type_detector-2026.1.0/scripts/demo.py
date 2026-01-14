"""Demo script for URL Content Type Detector."""

from url_content_type_detector import get_content_type, URLUtilsError

def main():
    """This is a demo script to test the URL Content Type Detector."""
    test_urls = [
        "https://www.example.com",
        "https://www.example.com/image.png",
        "https://www.example.com/document.pdf",
        "https://www.example.com/unknownfile.xyz",
        "https://krsahil.co.in/site/profile.webp",
        "https://avatars.githubusercontent.com/u/176153594?v=4",
    ]

    for url in test_urls:
        try:
            content_type = get_content_type(url)
            print(f"\n✅ URL: {url} -> Content Type: {content_type}")
        except URLUtilsError as e:
            print(f"\n❌ URL: {url} -> Error: {str(e)}")

if __name__ == "__main__":
    main()
