import asyncio
import logging
from collections.abc import Callable

from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.helpers.wait_for_network_settled import wait_for_network_settled

logger = logging.getLogger(__name__)


@wait_for_network_settled()
async def click_button_and_wait(
    page: Page,
    button_locator: Locator,
    click_delay: float = 0.5,
):
    """
    Click a button and wait briefly for content to load.

    Args:
        page: Playwright Page object
        button_locator: Locator for the button
        click_delay: Delay after clicking the button (in seconds)
    """
    await button_locator.scroll_into_view_if_needed()
    await button_locator.click(force=True)
    await asyncio.sleep(click_delay)


@wait_for_network_settled()
async def click_until_exhausted(
    page: Page,
    button_locator: Locator,
    heartbeat: Callable[[], None] = lambda: None,
    *,
    container_locator: Locator | None = None,
    max_clicks: int = 50,
    click_delay: float = 0.5,
    no_change_threshold: int = 0,
):
    """
    Repeatedly click a button until no new content appears or max clicks reached.

    This function is useful for "Load More" buttons or paginated content where you need to
    keep clicking until all content is loaded. It provides several stopping conditions:
    - Button becomes invisible/disabled
    - Maximum number of clicks reached
    - No change detected in container content (when container_locator is provided)

    Args:
        page (Page): Playwright Page object
        button_locator (Locator): Locator for the button to click repeatedly
        heartbeat (optional[Callable[[], None]]): Optional callback invoked after each click. Defaults to lambda: None.
        container_locator (optional[Locator]): Optional content container to detect changes. Defaults to None.
        max_clicks (optional[int]): Maximum number of times to click the button. Defaults to 50.
        click_delay (optional[float]): Delay after each click (in seconds). Defaults to 0.5.
        no_change_threshold (optional[int]): Minimum change in content size to continue clicking. Defaults to 0.

    Returns:
        None: Function completes when clicking is exhausted

    Examples:
        ```python Load All Items
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import click_until_exhausted
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/load-more")
            load_more_button = page.locator("main main button")  # Select the main button in the main content area.

            # Click until button disappears or is disabled
            await click_until_exhausted(
                page=page,
                button_locator=load_more_button,
                max_clicks=20
            )
            # Will keep clicking the button until the button disappears or is disabled or the max_clicks is reached.
        ```

        ```python Track Container Changes
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import click_until_exhausted
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/load-more")
            load_more_button = page.locator("aside button")  # Select the button in the sidebar.
            container = page.locator('xpath=//*[@id="root"]/div[1]/main/slot/div/aside/div/div/slot/slot')  # Watch the sidebar container to detect changes.
            # This will count the elements under the container given before each click and after, if the count is the same, the function will stop.
            click_count = 0

            def heartbeat_callback():
                nonlocal click_count
                click_count += 1
                print(f"Clicked {click_count} times")

            await click_until_exhausted(
                page=page,
                button_locator=load_more_button,
                container_locator=container,
                heartbeat=heartbeat_callback,
                max_clicks=30,
                click_delay=0.5,
                no_change_threshold=0
            )
            # Will keep clicking the button until the button disappears or is disabled or the max_clicks is reached or no more content is loaded.
        ```
    """

    prev_state = None
    if container_locator:
        prev_state = await get_container_state(container_locator)
        logger.info(f"Initial container state: {prev_state}")

    logger.info(f"Button matches: {await button_locator.count()}")
    for _ in range(max_clicks):
        heartbeat()

        if not (await button_locator.is_visible()):
            logger.info("Button not visible, stopping.")
            break

        if not (await button_locator.is_enabled()):
            logger.info("Button not enabled, stopping.")
            break

        await click_button_and_wait(
            page,
            button_locator,
            click_delay=click_delay,
        )

        if container_locator:
            current_state = await get_container_state(container_locator)
            logger.info(f"Current container state: {current_state}")
            if prev_state is not None and current_state - prev_state <= no_change_threshold:
                logger.info(f"No significant change in container state: {current_state} (previous: {prev_state})")
                break
            prev_state = current_state


async def get_container_state(container: Locator) -> int:
    """Measure container state by child count or scroll height."""
    if await container.count() > 0:
        # Prefer child element count if possible
        return await container.locator("> *").count()
    return await container.evaluate("element => element.scrollHeight")
