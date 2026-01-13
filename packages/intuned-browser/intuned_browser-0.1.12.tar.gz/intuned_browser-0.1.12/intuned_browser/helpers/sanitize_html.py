import re

from bs4 import BeautifulSoup
from bs4 import Comment


def sanitize_html(
    html: str,
    *,
    remove_scripts: bool = True,
    remove_styles: bool = True,
    remove_svgs: bool = True,
    remove_comments: bool = True,
    remove_long_attributes: bool = True,
    max_attribute_length: int = 500,
    preserve_attributes: list[str] | None = None,
    remove_empty_tags: bool = True,
    preserve_empty_tags: list[str] | None = None,
    minify_whitespace: bool = True,
) -> str:
    """
    Sanitizes and cleans HTML content by removing unwanted elements, attributes, and whitespace.
    Provides fine-grained control over each cleaning operation through configurable options.

    Args:
        html (str): The HTML content to sanitize
        remove_scripts (optional[bool]): Remove all `<script>` elements. Defaults to True.
        remove_styles (optional[bool]): Remove all `<style>` elements. Defaults to True.
        remove_svgs (optional[bool]): Remove all `<svg>` elements. Defaults to True.
        remove_comments (optional[bool]): Remove HTML comments. Defaults to True.
        remove_long_attributes (optional[bool]): Remove attributes longer than max_attribute_length. Defaults to True.
        max_attribute_length (optional[int]): Maximum length for attributes before removal. Defaults to 500.
        preserve_attributes (optional[list[str]]): List of attribute names to always preserve. Defaults to ["class", "src"].
        remove_empty_tags (optional[bool]): Remove empty tags (except preserved ones). Defaults to True.
        preserve_empty_tags (optional[list[str]]): List of tag names to preserve even when empty. Defaults to ["img"].
        minify_whitespace (optional[bool]): Remove extra whitespace between tags and empty lines. Defaults to True.

    Returns:
        str: The sanitized HTML string

    Examples:
        ```python Basic Sanitization
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import sanitize_html
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://books.toscrape.com")
            first_row = page.locator("ol.row").locator("li").first
            # Get the HTML of the first row.
            html = await first_row.inner_html()
            # Sanitize the HTML.
            sanitized_html = sanitize_html(html)
            # Log the sanitized HTML.
            print(sanitized_html)
            # Return the sanitized HTML.
            return sanitized_html
        ```
    """
    if preserve_attributes is None:
        preserve_attributes = ["class", "src"]
    if preserve_empty_tags is None:
        preserve_empty_tags = ["img"]

    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Remove specified elements
    elements_to_remove = []
    if remove_scripts:
        elements_to_remove.append("script")
    if remove_styles:
        elements_to_remove.append("style")
    if remove_svgs:
        elements_to_remove.append("svg")

    if elements_to_remove:
        for element in soup(elements_to_remove):
            element.decompose()

    # Remove HTML comments
    if remove_comments:
        for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
            comment.extract()

    # Remove long attributes and style attributes
    if remove_long_attributes:
        for tag in soup.find_all():
            for attr, value in list(tag.attrs.items()):  # type: ignore
                if attr in preserve_attributes:
                    continue
                if attr == "style" or len(str(value)) > max_attribute_length:
                    del tag.attrs[attr]  # type: ignore

    # Remove empty tags
    if remove_empty_tags:
        for tag in soup.find_all():
            if tag.name not in preserve_empty_tags and len(tag.get_text(strip=True)) == 0 and len(tag.find_all()) == 0:  # type: ignore
                tag.decompose()

    # Get the cleaned HTML as a string
    sanitized_html = str(soup)

    # Minify whitespace
    if minify_whitespace:
        # Remove white spaces between tags
        sanitized_html = sanitized_html.replace(">\n<", "><")
        # Remove multiple empty lines
        sanitized_html = re.sub(r"\n\s*\n", "\n", sanitized_html)
        # Remove multiple spaces
        sanitized_html = re.sub(r"\s+", " ", sanitized_html)

    return sanitized_html
