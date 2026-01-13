import asyncio
import functools
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import overload

from playwright.async_api import Page
from playwright.async_api import Request

logger = logging.getLogger(__name__)


# Overload 1: Wrapper pattern with page and func
@overload
async def wait_for_network_settled(
    *,
    page: Page,
    func: Callable[[], Awaitable[Any]],
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
) -> Any:
    """
    Executes a function and waits for network activity to settle before returning. This helper monitors network requests and waits until all network activity has completed.

    ## `wait_for_network_settled` vs `wait_for_dom_settled`
    - Use `wait_for_network_settled` when watching **network requests** (API calls, form submissions, resource loading)
    - Use [wait_for_dom_settled](../functions/wait_for_dom_settled) when watching **DOM mutations** (elements added/removed/modified, loading spinners, dynamic content injection)

    Overload:
        Wrapper Function Pattern

        This pattern executes a function and waits for network activity to settle before returning the result of the function.

    Args:
        page (Page): Playwright Page object to monitor network activity on.
        func (Callable[[], Any]): The async function to execute before waiting for network to settle. This function should contain the action that triggers network requests.
        timeout_s (optional[int]): Maximum seconds to wait for network to settle. If timeout is reached, logs a warning and continues. Defaults to 30.
        max_inflight_requests (optional[int]): Maximum number of ongoing requests to consider network as "settled". Defaults to 0 (waits for all requests).

    Returns:
        Any: The return value of the executed function.

    Examples:
        ```python Wrapper with Inline Function
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_network_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto('https://sandbox.intuned.dev/infinite-scroll')

            # Execute action and wait for network to settle
            async def scroll_action():
                # scroll to load more content
                await page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
                return "scrolled"

            result = await wait_for_network_settled(
                page=page,
                func=scroll_action,
                timeout_s=15,
                max_inflight_requests=0
            )
            print(result)  # "scrolled"
            return result
        ```

        ```python Click Link with Network Wait
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_network_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto('https://sandbox.intuned.dev/')

            # Click Object Extractors link and wait for page to load
            async def click_action():
                await page.get_by_text('Object Extractors').click()

            await wait_for_network_settled(
                page=page,
                func=click_action,
                timeout_s=10,
                max_inflight_requests=0
            )
            # Object Extractors page loaded
            title = await page.locator('div h2').inner_text()
            return title
        ```
    """
    ...


# Overload 2: Decorator without arguments
@overload
def wait_for_network_settled(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """
    Executes a function and waits for network activity to settle before returning. This helper monitors network requests and waits until all network activity has completed.

    ## `wait_for_network_settled` vs `wait_for_dom_settled`
    - Use `wait_for_network_settled` when watching **network requests** (API calls, form submissions, resource loading)
    - Use [wait_for_dom_settled](../functions/wait_for_dom_settled) when watching **DOM mutations** (elements added/removed/modified, loading spinners, dynamic content injection)

    Overload:
        Decorator

        This pattern decorates a function to automatically add network waiting functionality to the wrapped function.

    Args:
        func (Callable[[Page], Any]): The async function to decorate. Must accept a Page object as a parameter. If not provided, returns a parameterized decorator.
        timeout_s (optional[int]): Maximum seconds to wait for network to settle. If timeout is reached, logs a warning and continues (doesn't raise an error). Defaults to 30.
        max_inflight_requests (optional[int]): Maximum number of ongoing requests to consider network as "settled". Useful for pages with long-polling or streaming. Defaults to 0 (waits for all requests to complete).

    Returns:
        Callable: The decorated function that waits for network to settle after execution.

    Examples:
        ```python Simple Decorator
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_network_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/load-more")
            # Decorator without arguments (uses timeout_s=30, max_inflight_requests=0)
            @wait_for_network_settled
            async def click_load_more(page):
                await page.locator("main main button").click()
            # Automatically waits for network to settle after clicking
            await click_load_more(page)
            # Network has settled, data is loaded
        ```
    """
    ...


# Overload 3: Decorator factory with arguments
@overload
def wait_for_network_settled(
    *,
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    # Same docstring as Overload 2 - they share the "Decorator" tab
    ...


def wait_for_network_settled(
    *args: Any,
    **kwargs: Any,
) -> Any:
    # Case 1: Wrapper pattern with page and func as keyword arguments
    # await wait_for_network_settled(page=page, func=func, timeout_s=30)
    if "page" in kwargs and "func" in kwargs:
        page = kwargs["page"]
        func = kwargs["func"]
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)

        if not isinstance(page, Page):
            raise ValueError(
                "No Page object found in function arguments. 'page' parameter must be a Playwright Page object."
            )

        return _wait_for_network_settled_core(
            page=page,
            func=func,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    # Case 2: Decorator without arguments
    # @wait_for_network_settled
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], Page):
        func = args[0]
        return _create_decorated_function(func, timeout_s=30, max_inflight_requests=0)  # type: ignore

    # Case 3: Decorator factory with arguments (including empty parentheses)
    # @wait_for_network_settled() or @wait_for_network_settled(timeout_s=60, max_inflight_requests=0)
    if len(args) == 0 and "page" not in kwargs and "func" not in kwargs:
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)

        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            return _create_decorated_function(func, timeout_s=timeout_s, max_inflight_requests=max_inflight_requests)

        return decorator

    raise ValueError(
        "Invalid usage. Valid patterns:\n"
        "1. await wait_for_network_settled(page=page, func=func, timeout_s=30)\n"
        "2. @wait_for_network_settled or @wait_for_network_settled()\n"
        "3. @wait_for_network_settled(timeout_s=30, max_inflight_requests=0)\n"
    )


def _create_decorated_function(
    func: Callable[..., Awaitable[Any]],
    timeout_s: int,
    max_inflight_requests: int,
) -> Callable[..., Awaitable[Any]]:
    """Helper to create a decorated function with network waiting."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Find the page object in function arguments
        page = next((arg for arg in args if isinstance(arg, Page)), None)
        if page is None:
            page = kwargs.get("page")

        if not page or not isinstance(page, Page):
            logging.error(
                "No Page object found in function arguments. The decorated function must have a 'page' parameter or receive a Page object as an argument."
            )
            raise ValueError(
                "No Page object found in function arguments. The decorated function must have a 'page' parameter or receive a Page object as an argument."
            )

        async def func_with_args():
            return await func(*args, **kwargs)

        return await _wait_for_network_settled_core(
            page=page,
            func=func_with_args,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    return wrapper


async def _wait_for_network_settled_core(
    *,
    page: Page,
    func: Callable[..., Awaitable[Any]],
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
):
    """Core implementation of network settling logic."""
    if not isinstance(page, Page):
        raise ValueError("No Page object found in function arguments. Page parameter must be a Playwright Page object.")

    logging.debug(f"Page object: {page}")
    network_settled_event = asyncio.Event()
    is_timeout = False
    request_counter = 0
    action_done = False
    pending_requests: set[Request] = set()

    async def maybe_settle():
        if action_done and request_counter <= max_inflight_requests:
            network_settled_event.set()

    def on_request(request: Request):
        nonlocal request_counter
        request_counter += 1
        pending_requests.add(request)
        logging.debug(f"+[{request_counter}]: {request.url}")

    async def on_request_done(request: Request):
        nonlocal request_counter
        # Simulate asynchronous handling
        await asyncio.sleep(0)
        if request in pending_requests:
            request_counter -= 1
            pending_requests.discard(request)
            logging.debug(f"-[{request_counter}]: {request.url}")
            await maybe_settle()

    # Define listener functions to allow proper removal later
    async def handle_request_finished(req: Request):
        await on_request_done(req)

    async def handle_request_failed(req: Request):
        await on_request_done(req)

    # Add listeners
    page.on("request", on_request)
    page.on("requestfinished", handle_request_finished)
    page.on("requestfailed", handle_request_failed)

    async def timeout_task():
        nonlocal is_timeout
        await asyncio.sleep(timeout_s)
        is_timeout = True
        network_settled_event.set()

    try:
        # Execute the function and wait for network to settle
        result = await func()
        action_done = True
        await asyncio.sleep(0.5)
        await maybe_settle()
        timeout_task_handle = asyncio.create_task(timeout_task())
        while True:
            await network_settled_event.wait()
            await asyncio.sleep(0.5)
            if (action_done and request_counter <= max_inflight_requests) or is_timeout:
                if is_timeout:
                    logger.debug("Network did not settle within timeout.")
                else:
                    logger.debug("Network settled.")
                break
            else:
                network_settled_event = asyncio.Event()
        return result
    finally:
        # Remove listeners using the same function references
        page.remove_listener("request", on_request)
        page.remove_listener("requestfinished", handle_request_finished)
        page.remove_listener("requestfailed", handle_request_failed)
        try:
            timeout_task_handle.cancel()
        except Exception:
            pass
