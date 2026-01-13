import asyncio
from collections.abc import Callable
from typing import Union

from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.helpers.wait_for_network_settled import wait_for_network_settled


@wait_for_network_settled(max_inflight_requests=0, timeout_s=10)
async def _scroll_to_bottom(page: Page, scrollable: Union[Page, Locator]) -> int:
    """Scroll to the bottom of the container and return the new scroll height."""
    if isinstance(scrollable, Page):
        new_height = await scrollable.evaluate("""() => {
            window.scrollTo(0, document.body.scrollHeight);
            return document.body.scrollHeight;
        }""")
    else:
        new_height = await scrollable.evaluate("""
            element => {
                element.scrollTop = element.scrollHeight;
                return element.scrollHeight;
            }
        """)
    return new_height


async def scroll_to_load_content(
    source: Page | Locator,
    *,
    on_scroll_progress: Callable[[], None] = lambda: None,
    max_scrolls: int = 50,
    delay_s: float = 0.1,
    min_height_change: int = 100,
):
    """
    Automatically scrolls through infinite scroll content by repeatedly scrolling to the bottom
    until no new content loads or maximum scroll limit is reached.

    Args:
        source (Page | Locator): The Playwright Page or Locator to scroll.
        on_scroll_progress (optional[Callable]): Optional callback function to call during each scroll iteration. Defaults to lambda: None.
        max_scrolls (optional[int]): Maximum number of scroll attempts before stopping. Defaults to 50.
        delay_s (optional[float]): Delay in seconds between scroll attempts. Defaults to 0.1.
        min_height_change (optional[int]): Minimum height change in pixels required to continue scrolling. Defaults to 100. If the page has loaded all content and we still haven't reached the max_scrolls, the min_height_change will detect that no new content is loaded and stop the scrolling.

    Returns:
        None: Function completes when scrolling is finished

    Examples:
        ```python Basic Infinite Scroll handling
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import scroll_to_load_content
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Scroll through entire page content
            await page.goto("https://sandbox.intuned.dev/infinite-scroll")
            await scroll_to_load_content(
                source=page,
            )
            # Will keep scrolling until the page has loaded all content or the max_scrolls is reached.
        ```

        ```python Scroll Specific Container
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import scroll_to_load_content
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Scroll through a specific scrollable div
            await page.goto("https://docs.intunedhq.com/docs/00-getting-started/introduction")
            # This will scroll the sidebar content only and watch its height to change.
            container = page.locator("xpath=//div[@id='sidebar-content']")
            await scroll_to_load_content(
                source=container,
                max_scrolls=20
            )
            # Will keep scrolling until the sidebar content has loaded all content or the max_scrolls is reached.
        ```
    """
    scrollable = source
    if not scrollable:
        raise ValueError("scrollable is required")
    previous_height = -1
    scroll_count = 0
    page = source if isinstance(source, Page) else source.page
    while scroll_count < max_scrolls:
        on_scroll_progress()

        # Get current height and scroll to bottom
        current_height = await _scroll_to_bottom(page, scrollable)

        if abs(current_height - previous_height) < min_height_change:
            break

        # Update tracking variables
        previous_height = current_height
        scroll_count += 1

        # Wait for potential content load
        await asyncio.sleep(delay_s)
