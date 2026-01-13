import mdformat
from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.common.evaluate_with_intuned import evaluate_with_intuned


async def extract_markdown(source: Page | Locator) -> str:
    """
    Converts HTML content from a Playwright Page or Locator to semantic markdown format.

    Args:
        source (Page | Locator): The source of the HTML content. When a Page is provided, extracts from the entire page. When a Locator is provided, extracts from that specific element.

    Returns:
        str: The markdown representation of the HTML content

    Examples:
        ```python Extract Markdown from Locator
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import extract_markdown
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://books.toscrape.com/")
            header_locator = page.locator('h1').first  # First title on the page
            markdown = await extract_markdown(header_locator)  # Extract markdown from the first title
            print(markdown)
            return markdown
        ```

        ```python Extract Markdown from Page
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import extract_markdown
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/pdfs")
            markdown = await extract_markdown(page)
            print(markdown)
            return markdown
        ```
    """
    is_page = isinstance(source, Page)
    if is_page:
        handle = await source.locator("body").element_handle()
    else:
        handle = await source.element_handle()

    md = await evaluate_with_intuned(
        source,
        "(element) => window.__INTUNED__.convertElementToMarkdown(element)",
        handle.as_element(),
    )

    return mdformat.text(md)
