import asyncio
import logging
from typing import Literal
from typing import overload

from playwright.async_api import Page

from intuned_browser.ai.is_page_loaded import is_page_loaded
from intuned_browser.helpers.wait_for_network_settled import wait_for_network_settled

_timeout_padding = 3  # seconds


@overload
async def go_to_url(
    page: Page,
    url: str,
    *,
    timeout_s: int = 30,
    retries: int = 3,
    wait_for_load_state: str = "load",
    throw_on_timeout: bool = False,
    wait_for_load_using_ai: Literal[False] = False,
) -> None:
    """
    Navigates to a specified URL with enhanced reliability features including automatic retries with exponential backoff,
    intelligent timeout handling, and optional AI-powered loading verification.

    This function handles common navigation challenges by automatically retrying failed requests, detecting navigation hangs, and ensuring the page reaches a truly idle state.

    Overload:
        Without AI Loading Detection

        Use this overload for standard navigation without AI-powered loading detection.
    Args:
        page (Page): The Playwright Page object to navigate.
        url (str): The URL to navigate to.
        timeout_s (optional[int]): Maximum navigation time in seconds. Defaults to 30.
        retries (optional[int]): Number of retry attempts with exponential backoff (factor: 2). Defaults to 3.
        wait_for_load_state (optional[Literal["load", "domcontentloaded", "networkidle", "commit"]]): When to consider navigation succeeded. Defaults to "load".
        throw_on_timeout (optional[bool]): Whether to raise an error on navigation timeout. When False, the function returns without throwing, allowing continued execution. Defaults to False.
        wait_for_load_using_ai (optional[bool]): Set to False to disable AI-powered loading checks. Defaults to False.

    Returns:
        None: Function completes when navigation is finished or fails after retries.

    Examples:
        ```python Without options
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import go_to_url
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await go_to_url(
                page,
                url='https://sandbox.intuned.dev/'
            )
            # At this point, go_to_url has waited for the page to be loaded and the network requests to be settled.
        ```

        ```python With options
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import go_to_url
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await go_to_url(
                page,
                url='https://intunedhq.com',
                wait_for_load_state="domcontentloaded",  # Faster than "load" state. The function automatically waits for the page to settle.
                throw_on_timeout=True,
                timeout_s=10,
                retries=3
            )
            # At this point, DOM content is loaded and go_to_url has waited for network requests to settle.
        ```

    """
    ...


@overload
async def go_to_url(
    page: Page,
    url: str,
    *,
    timeout_s: int = 30,
    retries: int = 3,
    wait_for_load_state: str = "load",
    throw_on_timeout: bool = False,
    wait_for_load_using_ai: Literal[True],
    model: str | None = "gpt-5-mini-2025-08-07",
    api_key: str | None = None,
) -> None:
    """
    Navigates to a specified URL with enhanced reliability features including automatic retries with exponential backoff,
    intelligent timeout handling, and optional AI-powered loading verification.

    This function handles common navigation challenges by automatically retrying failed requests, detecting navigation hangs, and ensuring the page reaches a truly idle state.

    Overload:
        With AI Loading Detection

        Use this overload when you need AI vision to verify the page is fully loaded by checking for loading spinners, blank content, or incomplete states.
    Args:
        page (Page): The Playwright Page object to navigate.
        url (str): The URL to navigate to.
        timeout_s (optional[int]): Maximum navigation time in seconds. Defaults to 30.
        retries (optional[int]): Number of retry attempts with exponential backoff (factor: 2). Defaults to 3.
        wait_for_load_state (optional[Literal["load", "domcontentloaded", "networkidle", "commit"]]): When to consider navigation succeeded. Defaults to "load".
        throw_on_timeout (optional[bool]): Whether to raise an error on navigation timeout. When False, the function returns without throwing, allowing continued execution. Defaults to False.
        wait_for_load_using_ai (Literal[True]): Must be set to True to use this AI-powered overload. When true, uses AI vision to verify the page is fully loaded by checking for loading spinners, blank content, or incomplete states. Retries up to 3 times with 5-second delays. Check [is_page_loaded](../../ai/functions/is_page_loaded) for more details on the AI loading verification.
        model (optional[str]): AI model to use for loading verification. Defaults to "gpt-5-mini-2025-08-07".
        api_key (optional[str]): Optional API key for the AI check. Defaults to None.

    Returns:
        None: Function completes when navigation is finished or fails after retries.

    Examples:
        ```python With AI Loading Detection
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import go_to_url
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await go_to_url(
                page,
                url='https://intunedhq.com',
                wait_for_load_using_ai=True,
                model="gpt-4o"
            )
            # The page is loaded and ready to use.
            # If the AI check fails, the method won't throw even if throw_on_timeout is true.
            # It only throws if the page times out reaching the default load state and throw_on_timeout is true.
        ```
    """
    ...


@wait_for_network_settled()
async def go_to_url(
    page: Page,
    url: str,
    *,
    timeout_s: int = 30,
    retries: int = 3,
    wait_for_load_state: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
    throw_on_timeout: bool = False,
    wait_for_load_using_ai: bool = False,
    model: str = "gpt-5-mini-2025-08-07",
    api_key: str | None = None,
) -> None:
    for i in range(retries):
        try:
            current_timeout = (timeout_s * (2**i)) * 1000
            try:
                await asyncio.wait_for(
                    page.goto(url, timeout=current_timeout, wait_until=wait_for_load_state),
                    timeout=current_timeout / 1000 + _timeout_padding,
                )
            except asyncio.TimeoutError as e:  # noqa
                raise asyncio.TimeoutError(  # noqa
                    f"Page.goto timed out but did not throw an error. Consider using a proxy.\n"
                    f"(URL: {url}, timeout: {timeout_s * 1000}ms)"
                ) from e
            break
        except (Exception, asyncio.TimeoutError) as e:  # noqa
            await asyncio.sleep(2)
            if i == retries - 1:
                logging.error(f"Failed to open URL: {url}. Error: {e}")
                if throw_on_timeout:
                    raise e

    if not wait_for_load_using_ai:
        return

    # Retry AI page loading check up to 'retries' times
    for i in range(retries):
        is_loaded = False

        try:
            is_loaded = await is_page_loaded(page, model=model, timeout_s=3, api_key=api_key)
            logging.debug(f"is_loaded (attempt {i + 1}/{retries}): {is_loaded}")

            if is_loaded:
                return
        except Exception as e:
            logging.debug(f"Failed to check if page is loaded: {url}. Error: {e}, retrying...")
            is_loaded = False

        # If this was the last attempt and page still not loaded, throw error
        if i == retries - 1:
            logging.warning(f"Page never loaded: {url}")
            return

        # Wait before next retry (not needed after last attempt since we return/raise above)
        await asyncio.sleep(5)
