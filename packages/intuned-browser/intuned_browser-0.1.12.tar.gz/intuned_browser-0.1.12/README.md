---
title: "Python SDK"
sidebarTitle: "intuned_browser"
icon: cube
---

Browser automation helpers for Python, built on [Playwright](https://playwright.dev/). This package provides utilities for common automation tasks—AI-powered data extraction, navigation with retries, pagination handling, and more.

## Installation

```bash
pip install intuned-browser
```

<Note>
When using [Intuned](https://intunedhq.com), this package is pre-installed in every Python project.
</Note>

## Quick example

```python
from typing import TypedDict

from playwright.async_api import Page
from intuned_browser.ai import extract_structured_data, is_page_loaded
from intuned_browser.helpers import go_to_url

class Params(TypedDict):
    pass

async def automation(page: Page, params:Params, **kwargs):
    await go_to_url(page, "https://books.toscrape.com")
    loaded = await is_page_loaded(page)
    if not loaded:
      raise ValueError("Page is not loaded, can not extract data")

    # Extract all book listings from the page
    books = await extract_structured_data(
        source=page,
        data_schema={
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "price": {"type": "string"}
                        }
                    }
                }
            }
        },
        prompt="Extract all book listings with their titles and prices",
        strategy="HTML",
        model="claude-haiku-4-5-20251001"
    )

    return books
```

## AI module

AI-powered utilities for data extraction and page analysis. These functions use AI and incur costs.

| Function | Description |
| --- | --- |
| [`extract_structured_data`](./ai/functions/extract_structured_data) | Extract structured data from pages using AI with schema validation |
| [`is_page_loaded`](./ai/functions/is_page_loaded) | Detect when a page has finished loading |

<Tip>AI functions support caching and matching to reduce costs.</Tip>

## Helpers module

| Function | Description |
| --- | --- |
| [`go_to_url`](./helpers/functions/go_to_url) | Navigate with automatic retries and error handling |
| [`wait_for_network_settled`](./helpers/functions/wait_for_network_settled) | Wait for network requests to complete |
| [`wait_for_dom_settled`](./helpers/functions/wait_for_dom_settled) | Wait for DOM mutations to finish |
| [`scroll_to_load_content`](./helpers/functions/scroll_to_load_content) | Load infinite-scroll content |
| [`click_until_exhausted`](./helpers/functions/click_until_exhausted) | Click "Load More" buttons until all content loads |
| [`extract_markdown`](./helpers/functions/extract_markdown) | Convert pages to markdown |
| [`download_file`](./helpers/functions/download_file) | Download files with different triggers |
| [`save_file_to_s3`](./helpers/functions/save_file_to_s3) | Download and upload files to S3 |
| [`upload_file_to_s3`](./helpers/functions/upload_file_to_s3) | Upload files with custom S3 configurations |
| [`filter_empty_values`](./helpers/functions/filter_empty_values) | Remove empty values from data |
| [`validate_data_using_schema`](./helpers/functions/validate_data_using_schema) | Validate data against schemas |
| [`process_date`](./helpers/functions/process_date) | Parse and normalize dates |
| [`sanitize_html`](./helpers/functions/sanitize_html) | Clean and sanitize HTML |
| [`resolve_url`](./helpers/functions/resolve_url) | Resolve relative URLs to absolute paths |

## Requirements

- Python 3.8+
- Playwright (`pip install playwright && playwright install`)
- For AI functions: API key for your AI provider (set via environment variable or function parameter)
