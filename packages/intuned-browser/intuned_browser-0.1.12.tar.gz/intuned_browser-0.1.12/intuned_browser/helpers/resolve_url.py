from typing import overload
from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from playwright.async_api import Locator
from playwright.async_api import Page


@overload
async def resolve_url(
    *,
    url: str,
    base_url: str,
) -> str:
    """
    Converts any URL source to an absolute, properly encoded URL.

    Overload:
        Base URL String

        Combines a relative URL with a base URL string. Use when you have an explicit base URL string to resolve relative paths against.

    Args:
        url (str): The relative or absolute URL to resolve.
        base_url (str): Base URL string to resolve relative URLs against.

    Returns:
        str: The absolute, properly encoded URL string

    Examples:
        ```python Resolve from Base URL String
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import resolve_url
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Resolve from base URL string
            absolute_url = await resolve_url(
                url="/lists/table",
                base_url="https://sandbox.intuned.dev"
            )
            # Returns: "https://sandbox.intuned.dev/lists/table"
            print(absolute_url)
            return absolute_url
        ```
    """
    ...


@overload
async def resolve_url(
    *,
    url: str,
    page: Page,
) -> str:
    """
    Converts any URL source to an absolute, properly encoded URL.

    Overload:
        Current Page's URL

        Uses the current page's URL as the base URL. Use when resolving URLs relative to the current page.

    Args:
        url (str): The relative or absolute URL to resolve.
        page (Page): Playwright Page object to extract base URL from. The current page URL will be used as the base URL.

    Returns:
        str: The absolute, properly encoded URL string

    Examples:
        ```python Resolve from the Current Page's URL
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import resolve_url
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/")
            # Resolve from the current page's URL
            absolute_url = await resolve_url(
                url="/lists/table",
                page=page
            )
            # Returns: "https://sandbox.intuned.dev/lists/table"
            print(absolute_url)
            return absolute_url
        ```
    """
    ...


@overload
async def resolve_url(
    *,
    url: Locator,
) -> str:
    """
    Converts any URL source to an absolute, properly encoded URL.

    Overload:
        Anchor Elements

        Extracts the href attribute from a Playwright Locator pointing to an anchor element. Use when extracting and resolving URLs from anchor (`<a>`) elements.

    Args:
        url (Locator): Playwright Locator pointing to an anchor element. The href attribute will be extracted and resolved relative to the current page.

    Returns:
        str: The absolute, properly encoded URL string

    Examples:
        ```python Resolve from Anchor Element
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import resolve_url
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/")
            # Resolve from Anchor Element
            absolute_url = await resolve_url(
                url=page.locator("xpath=//a[normalize-space()='Steps Form']"),
            )
            # Returns: "https://sandbox.intuned.dev/steps-form"
            print(absolute_url)
            return absolute_url
        ```
    """
    ...


async def resolve_url(
    *,
    url: str | Locator,
    base_url: str | None = None,
    page: Page | None = None,
) -> str:
    # Handle Locator/ElementHandle case
    if isinstance(url, (Locator)):
        if base_url is not None or page is not None:
            raise ValueError("base_url and page parameters are not needed when url is Locator")

        # Validate it's an anchor element
        element_name = await url.evaluate("(element) => element.tagName")
        if element_name != "A":
            raise ValueError(f"Expected an anchor element, got {element_name}")

        # Extract absolute href (browser automatically resolves relative URLs)
        return await url.evaluate("(element) => element.href")

    # Handle string URL case
    elif isinstance(url, str):
        # Validate that exactly one of base_url or page is provided
        if base_url is not None and page is not None:
            raise ValueError("Cannot provide both 'base_url' and 'page' parameters. Please provide only one.")
        if base_url is None and page is None:
            raise ValueError("Must provide either 'base_url' or 'page' parameter when url is a string.")

        relative_url = url

        # Extract base URL from Page object or use string directly
        if page is not None:
            parsed_url = urlparse(page.url)
            base_url_str = f"{parsed_url.scheme}://{parsed_url.netloc}"
        else:
            base_url_str = base_url

        # Check if the URL is already absolute
        parsed_relative = urlparse(relative_url)
        if parsed_relative.scheme and parsed_relative.netloc:
            return relative_url

        # Join base and relative URLs
        full_url = urljoin(base_url_str, relative_url) if base_url_str else ""

        # Parse the full URL
        parsed_full = urlparse(full_url)

        # Encode the path and query
        encoded_path = quote(parsed_full.path, safe="/%")
        encoded_query = quote(parsed_full.query, safe="=&%")

        # Reconstruct the URL with encoded components
        return urlunparse(
            (
                parsed_full.scheme,
                parsed_full.netloc,
                encoded_path,
                parsed_full.params,
                encoded_query,
                parsed_full.fragment,
            )
        )

    else:
        raise TypeError(f"url must be str, Locator, got {type(url)}")
