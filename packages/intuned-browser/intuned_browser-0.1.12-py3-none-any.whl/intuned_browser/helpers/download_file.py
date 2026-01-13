import base64
import inspect
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from contextvars import copy_context
from typing import Union

import validators
from playwright.async_api import Download
from playwright.async_api import ElementHandle
from playwright.async_api import Locator
from playwright.async_api import Page
from playwright.async_api import TimeoutError
from typing_extensions import TypeGuard

from intuned_browser.helpers.resolve_url import resolve_url
from intuned_browser.helpers.utils.get_mode import is_generate_code_mode

logger = logging.getLogger(__name__)


type Trigger = str | Locator | Callable[[Page], None] | Callable[[Page], Awaitable[None]]
"""
A union type representing different methods to trigger file downloads in web automation.

This type alias standardizes how download operations can be initiated, providing
multiple approaches to suit different automation scenarios.

Type Information:
    - `str`: Direct URL string to download from
    - `Locator`: Playwright Locator object pointing to a clickable download element
    - `Callable[[Page], None]` | `Callable[[Page], Awaitable[None]]`: Custom async function that takes a Page and triggers the download

Examples:
    ```python URL String Trigger
    from typing import TypedDict
    from playwright.async_api import Page
    from intuned_browser import download_file
    class Params(TypedDict):
        pass
    async def automation(page: Page, params: Params, **_kwargs):
        # Direct download from URL
        download = await download_file(
            page,
            trigger="https://intuned-docs-public-images.s3.amazonaws.com/32UP83A_ENG_US.pdf"
        )
    ```

    ```python Locator Trigger
    from typing import TypedDict
    from playwright.async_api import Page
    from intuned_browser import download_file
    class Params(TypedDict):
        pass
    async def automation(page: Page, params: Params, **_kwargs):
        await page.goto("https://sandbox.intuned.dev/pdfs")
        # Click a download button
        download = await download_file(
            page,
            trigger=page.locator("xpath=//tbody/tr[1]//*[name()='svg']")
        )
    ```

    ```python Callback Trigger
    from typing import TypedDict
    from playwright.async_api import Page
    from intuned_browser import download_file
    class Params(TypedDict):
        pass
    async def automation(page: Page, params: Params, **_kwargs):
        await page.goto("https://sandbox.intuned.dev/pdfs")
        # Custom download logic
        download = await download_file(
            page,
            trigger=lambda p: p.locator("xpath=//tbody/tr[1]//*[name()='svg']").click()
        )
    ```
"""


async def get_absolute_url(page: Page, url: str) -> str:
    try:
        url_locator = page.locator(f"a[href='{url}']")
        if await url_locator.count() > 0:
            return await url_locator.evaluate("(el) => el.href")
    except Exception:
        pass
    return await resolve_url(url=url, page=page)


async def download_file(
    page: Page,
    trigger: Trigger,
    *,
    timeout_s: int = 5,
) -> Download:
    """
    Downloads a file from a web page using various trigger methods. This function provides three flexible ways to initiate file downloads:

    - **URL**: Creates a new page, navigates to the URL, waits for download, then automatically closes the page. Ideal for direct download links.
    - **Locator**: Uses the current page to click the element and capture the resulting download. Perfect for download buttons or interactive elements.
    - **Callback**: Executes the provided function with the page object and captures the first triggered download. Offers maximum flexibility for complex download scenarios.

    Args:
        page (Page): The Playwright Page object to use for the download.
        trigger (Trigger): The [Trigger](../type-references/Trigger) method to initiate the download.
        timeout_s (optional[int]): Maximum time in seconds to wait for download to start. Defaults to 5.

    Returns:
        Download: The [Playwright Download object](https://playwright.dev/python/docs/api/class-download) representing the downloaded file.

    Examples:
        ```python Download from direct URL
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import download_file
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Download from a direct URL, this will open the url and automatically download the content in it.
            download = await download_file(
                page,
                trigger="https://intuned-docs-public-images.s3.amazonaws.com/32UP83A_ENG_US.pdf"
            )
            file_name = download.suggested_filename
            return file_name
        ```

        ```python Locator Trigger
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import download_file
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/pdfs")
            download = await download_file(
                page,
                trigger=page.locator("xpath=//tbody/tr[1]//*[name()='svg']")
            )
            file_name = download.suggested_filename
            return file_name
        ```

        ```python Callback Trigger
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import download_file
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/pdfs")
            download = await download_file(
                page,
                trigger=lambda page: page.locator("xpath=//tbody/tr[1]//*[name()='svg']").click()
            )
            file_name = download.suggested_filename
            return file_name
        ```
    """
    page_to_download_from = page
    should_close_after_download = False
    is_invalid_url = False

    def is_url(trigger) -> TypeGuard[str]:
        return isinstance(trigger, str)

    def is_locator(trigger) -> TypeGuard[Union[Locator, ElementHandle]]:
        return isinstance(trigger, Union[Locator, ElementHandle])

    def is_callable(trigger) -> TypeGuard[Union[Callable[[Page], None], Callable[[Page], Awaitable[None]]]]:
        return callable(trigger)

    ctx = copy_context()

    def on_new_page(page: Page) -> None:
        """Callback function to handle new page creation."""

        def new_page_logic():
            logger.info(f"Detected new page opened while processing the download with URL: {page.url}")

            def download_handler(download):
                ctx.run(
                    lambda: logger.info(
                        f"Detected download with URL: {download.url} happened inside page with URL: {page.url} Note that this page is not the original page that called the function."
                    )
                )

            page.on("download", download_handler)

        ctx.run(new_page_logic)

    if is_url(trigger):
        page_to_download_from = await page.context.new_page()
        should_close_after_download = True

    logger.info(f"start to download from {trigger}")
    page_to_download_from.context.on("page", on_new_page)

    try:
        async with page_to_download_from.expect_download(timeout=timeout_s * 1000 + 1000) as download_info:
            await page_to_download_from.evaluate(
                "(() => {window.waitForPrintDialog = new Promise(f => window.print = f);})()"
            )

            if is_url(trigger):
                full_url = await get_absolute_url(page=page, url=trigger)
                is_valid = validators.url(full_url)
                if not is_valid:
                    logger.warning(f"Url is not valid, the download might not be triggered correctly. {full_url}")
                    is_invalid_url = True
                try:
                    response = await page_to_download_from.goto(full_url, wait_until="load", timeout=timeout_s * 1000)
                    content_type = response.headers.get("content-type", "") if response else ""

                    if content_type.startswith("image/"):
                        await page_to_download_from.evaluate(f"""
                            const link = document.createElement('a');
                            link.href = '{full_url}';
                            link.download = '';  // This forces download
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            """)
                except Exception:
                    pass
            if is_locator(trigger):
                await trigger.click()
                try:
                    await page_to_download_from.wait_for_function("window.waitForPrintDialog", timeout=1000)
                    pdf = await page_to_download_from.pdf(format="A4")
                    pdf_base64 = base64.b64encode(pdf).decode("utf-8")
                    await page_to_download_from.evaluate(f"""
                        const dataUrl = 'data:application/pdf;base64,{pdf_base64}';
                        const link = document.createElement('a');
                        link.href = dataUrl;
                        link.download = 'print.pdf';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    """)
                except TimeoutError:
                    # Print dialog was not triggered, normal download will proceed
                    pass
            if is_callable(trigger):
                result = trigger(page)
                if inspect.iscoroutine(result):
                    await result
                try:
                    await page_to_download_from.wait_for_function("window.waitForPrintDialog", timeout=1000)
                    pdf = await page_to_download_from.pdf(format="A4")
                    pdf_base64 = base64.b64encode(pdf).decode("utf-8")
                    await page_to_download_from.evaluate(f"""
                        const dataUrl = 'data:application/pdf;base64,{pdf_base64}';
                        const link = document.createElement('a');
                        link.href = dataUrl;
                        link.download = 'print.pdf';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    """)
                except TimeoutError:
                    # Print dialog was not triggered, normal download will proceed
                    pass
    except TimeoutError as e:
        if is_url(trigger) and not is_invalid_url:
            # Check if page is a 404 page by looking for common 404 patterns
            not_found_patterns = [
                "404",
                "not found",
                "page not found",
                "page doesn't exist",
                "page does not exist",
                "resource not found",
            ]
            for pattern in not_found_patterns:
                if await page_to_download_from.get_by_text(pattern, exact=False).count() > 0:
                    page_to_download_from.context.remove_listener("page", on_new_page)
                    raise TimeoutError(f"Download timeout for url:{trigger}. Page appears to be a 404 page.") from e
            raise TimeoutError(f"Download timeout for url:{trigger}. Download was never triggered.") from e
        if is_locator(trigger):
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(f"Download timeout for locator:{trigger}. Download was never triggered.") from e
        if is_callable(trigger):
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(f"Download timeout for callable:{trigger}. Download was never triggered.") from e
        if is_url(trigger) and is_invalid_url:
            page_to_download_from.context.remove_listener("page", on_new_page)
            raise TimeoutError(f"Url is not valid, the download did not trigger correctly. {trigger}") from e
    finally:
        if should_close_after_download:
            try:
                await page_to_download_from.close()
            except Exception:
                pass

    download = await download_info.value
    if is_generate_code_mode():
        await download.cancel()

    logger.info(f"Downloaded file successfully by {trigger}")
    page_to_download_from.context.remove_listener("page", on_new_page)

    return download
