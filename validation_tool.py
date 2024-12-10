import json
from schema import ScrapedData

def validate_json(response):
    try:
        # Simulate an API response
        scraped_data = ScrapedData(**response)
        print("JSON is valid!")
        print(json.dumps(scraped_data.dict(), indent=2))
    except Exception as e:
        print(f"Invalid JSON: {e}")

# Example response to validate
example_response = {
    "page_title": "Example Title",
    "metadata": {
        "description": "An example meta description.",
        "keywords": "example, test, scrape",
        "author": "John Doe"
    },
    "headings": ["Welcome", "Features"],
    "paragraphs": ["This is a sample paragraph."],
    "links": [{"href": "https://example.com", "text": "Example"}],
    "images": [{"src": "https://example.com/image.jpg", "alt": "Sample Image"}]
}

# Validate the example JSON
validate_json(example_response)