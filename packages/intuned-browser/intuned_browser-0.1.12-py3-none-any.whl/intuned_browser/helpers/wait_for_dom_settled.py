import asyncio
import functools
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import overload
from typing import Union

from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.helpers.frame_utils import find_all_iframes_list
from intuned_browser.helpers.frame_utils import get_container_frame

logger = logging.getLogger(__name__)


# Overload 1: Direct call with source only (callable pattern - positional)
@overload
async def wait_for_dom_settled(
    source: Page | Locator,
    *,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> bool:
    """
    Waits for DOM mutations to settle. This helper uses a MutationObserver to monitor DOM changes and waits until the DOM has been stable (no mutations) for the specified settle_duration.

    ## `wait_for_dom_settled` vs `wait_for_network_settled`

    - Use `wait_for_dom_settled` when watching **DOM mutations** (elements added/removed/modified, loading spinners, dynamic content injection)
    - Use [wait_for_network_settled](../functions/wait_for_network_settled) when watching **network requests** (API calls, form submissions, resource loading)

    Overload:
        Direct Function Call (Callable Pattern)

        This pattern waits for existing DOM changes to complete without triggering any new actions. Useful after navigation or for waiting for animations.

    Args:
        source (Page | Locator): Playwright Page or Locator object to monitor for DOM changes. Can be passed as positional or keyword argument. Use Page to monitor entire document, or Locator to watch specific element.
        settle_duration (optional[float]): Duration in seconds that the DOM must remain stable (no mutations) to be considered "settled". Defaults to 0.5.
        timeout_s (optional[float]): Maximum seconds to wait for DOM to settle before raising an error. Defaults to 30.0.

    Returns:
        bool: True if DOM settled successfully within timeout.

    Raises:
        TimeoutError: If DOM doesn't settle within timeout_s.

    Examples:
        ```python Wait After Navigation
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_dom_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Navigate to page with dynamic content
            await page.goto('https://sandbox.intuned.dev/lists/table')

            # Wait for all DOM mutations to complete
            settled = await wait_for_dom_settled(
                source=page,
                settle_duration=1.0,
                timeout_s=20
            )

            if settled:
                # DOM is stable, safe to extract data
                rows = await page.locator('table tr').all()
                return len(rows)
            return 0
        ```

        ```python Watch Specific Container
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_dom_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/lists/table")

            # Only watch table container (ignore header/footer changes)
            table = page.locator("table")
            settled = await wait_for_dom_settled(
                source=table,
                settle_duration=0.8,
                timeout_s=15,
            )

            if settled:
                # Table has finished loading
                rows = await table.locator('tr').count()
                return rows
            return 0
        ```
    """
    ...


# Overload 2: Wrapper pattern with source and func
@overload
async def wait_for_dom_settled(
    *,
    source: Page | Locator,
    func: Callable[[], Awaitable[Any]],
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> Any:
    """
    Waits for DOM mutations to settle. This helper uses a MutationObserver to monitor DOM changes and waits until the DOM has been stable (no mutations) for the specified settle_duration.

    ## `wait_for_dom_settled` vs `wait_for_network_settled`

    - Use `wait_for_dom_settled` when watching **DOM mutations** (elements added/removed/modified, loading spinners, dynamic content injection)
    - Use [wait_for_network_settled](../functions/wait_for_network_settled) when watching **network requests** (API calls, form submissions, resource loading)

    Overload:
        Wrapper Function Pattern

        This pattern executes a function and waits for DOM mutations to settle before returning.

    Args:
        source (Page | Locator): Playwright Page or Locator object to monitor for DOM changes. Use Page for entire document, Locator for specific element.
        func (Callable[[], Any]): The async function to execute before waiting for DOM to settle. This function should contain the action that triggers DOM changes.
        settle_duration (optional[float]): Duration in seconds that the DOM must remain stable (no mutations) to be considered "settled". Defaults to 0.5.
        timeout_s (optional[float]): Maximum seconds to wait for DOM to settle before raising an error. Defaults to 30.0.

    Returns:
        Any: The return value of the executed function.

    Raises:
        TimeoutError: If DOM doesn't settle within timeout_s.

    Examples:
        ```python Wrapper with Inline Function
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_dom_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/lists/table")
            # Define action inline
            async def select_card():
                await page.locator("xpath=//button[@id='radix-:r0:-trigger-card']").click()
                return "card selected"
            # Execute and wait for DOM to settle
            result = await wait_for_dom_settled(
                source=page,
                func=select_card,
                settle_duration=1.0,
                timeout_s=15
            )
            return result
        ```
        ```python Wrapper with Specific Element
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_dom_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev")
            # Monitor only the data table, not the entire page
            data_table = page.locator("table")
            async def click_list_extractors():
                await page.get_by_text("List Extractors").click()
                return "list extractors clicked"
            await wait_for_dom_settled(
                source=data_table,  # Only watch this element
                func=click_list_extractors,
                settle_duration=0.8,
                timeout_s=10
            )
            # Table has finished updating
            rows = await data_table.locator("tr").count()
            return rows
        ```
        ```python Wrapper with Lambda
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_dom_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/load-more")
            # Quick one-off action
            await wait_for_dom_settled(
                source=page,
                func=lambda: page.locator("main main button").click(),
                settle_duration=0.5,
                timeout_s=10
            )
            # More items loaded
            items = await page.locator(".item").count()
            return items
        ```
    """
    ...


# Overload 3: Decorator without arguments
@overload
def wait_for_dom_settled(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """
    Waits for DOM mutations to settle. This helper uses a MutationObserver to monitor DOM changes and waits until the DOM has been stable (no mutations) for the specified settle_duration.

    ## `wait_for_dom_settled` vs `wait_for_network_settled`

    - Use `wait_for_dom_settled` when watching **DOM mutations** (elements added/removed/modified, loading spinners, dynamic content injection)
    - Use [wait_for_network_settled](../functions/wait_for_network_settled) when watching **network requests** (API calls, form submissions, resource loading)

    Overload:
        Decorator

        This pattern decorates a function to automatically wait for DOM to settle after execution.

    Args:
        func (Callable[[Page], Any] | Callable[[Locator], Any]): The async function to decorate. Must accept a Page or Locator object as a parameter. If not provided, returns a parameterized decorator.
        settle_duration (optional[float]): Duration in seconds that the DOM must remain stable (no mutations) to be considered "settled". Increase for slow animations. Defaults to 0.5.
        timeout_s (optional[float]): Maximum seconds to wait for DOM to settle before timing out. Raises an error if timeout is reached. Defaults to 30.0.

    Returns:
        Callable: The decorated function that waits for DOM to settle after execution.

    Notes:
        - The decorated function **MUST** have a `page` or `source` parameter (or receive a Locator)
        - Can monitor entire page (Page) or specific elements (Locator)
        - DOM is "settled" when no mutations occur for settle_duration seconds
        - Raises error on timeout (unlike wait_for_network_settled which logs warning)
        - Use Locator to ignore unrelated DOM changes on other parts of the page

    Examples:
        ```python Simple Decorator
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import wait_for_dom_settled
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/load-more")
            # Decorator without arguments (uses settle_duration=0.5, timeout_s=30.0)
            @wait_for_dom_settled
            async def load_more_content(page):
                await page.locator("main main button").click()
            # Automatically waits for DOM to settle after clicking
            await load_more_content(page)
            # DOM has settled, new content is loaded
        ```
    """
    ...


# Overload 4: Decorator factory with arguments
@overload
def wait_for_dom_settled(
    *,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    # Same docstring as Overload 3 - they share the "Decorator" tab
    ...


def wait_for_dom_settled(
    *args: Any,
    **kwargs: Any,
) -> Any:
    # Case 1a: Direct call with source only (callable pattern - positional)
    # await wait_for_dom_settled(source, settle_duration=0.5, timeout_s=30)
    if len(args) == 1 and isinstance(args[0], (Page, Locator)):
        source = args[0]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)
        return _wait_for_dom_settled_original(
            source=source,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 1b: Direct call with source only (callable pattern - keyword)
    # await wait_for_dom_settled(source=page, settle_duration=0.5, timeout_s=30)
    if "source" in kwargs and "func" not in kwargs and len(args) == 0:
        source = kwargs["source"]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)

        if not isinstance(source, (Page, Locator)):
            raise ValueError(
                "No Page or Locator object found in function arguments. 'source' parameter must be a Playwright Page or Locator object."
            )

        return _wait_for_dom_settled_original(
            source=source,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 2: Wrapper pattern with source and func as keyword arguments
    # await wait_for_dom_settled(source=source, func=func, settle_duration=0.5, timeout_s=30)
    if "source" in kwargs and "func" in kwargs:
        source = kwargs["source"]
        func = kwargs["func"]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)

        if not isinstance(source, (Page, Locator)):
            raise ValueError(
                "No Page or Locator object found in function arguments. 'source' parameter must be a Playwright Page or Locator object."
            )

        return _wait_for_dom_settled_core(
            source=source,
            func=func,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 3: Decorator without arguments
    # @wait_for_dom_settled
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], (Page, Locator)):
        func = args[0]
        return _create_decorated_function(func, settle_duration=0.5, timeout_s=30.0)  # type: ignore

    # Case 4: Decorator factory with arguments (including empty parentheses)
    # @wait_for_dom_settled() or @wait_for_dom_settled(settle_duration=1.0, timeout_s=30)
    if len(args) == 0 and "source" not in kwargs and "func" not in kwargs:
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)

        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            return _create_decorated_function(func, settle_duration=settle_duration, timeout_s=timeout_s)

        return decorator

    raise ValueError(
        "Invalid usage. Valid patterns:\n"
        "1. await wait_for_dom_settled(source, settle_duration=0.5, timeout_s=30) or await wait_for_dom_settled(source=source, settle_duration=0.5, timeout_s=30)\n"
        "2. await wait_for_dom_settled(source=source, func=func, settle_duration=0.5, timeout_s=30)\n"
        "3. @wait_for_dom_settled or @wait_for_dom_settled()\n"
        "4. @wait_for_dom_settled(settle_duration=1.0, timeout_s=30)"
    )


def _create_decorated_function(
    func: Callable[..., Awaitable[Any]],
    settle_duration: float,
    timeout_s: float,
) -> Callable[..., Awaitable[Any]]:
    """Helper to create a decorated function with DOM waiting."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Find the Page or Locator object in function arguments
        source_obj = None
        for arg in args:
            if isinstance(arg, (Page, Locator)):
                source_obj = arg
                break
        if source_obj is None:
            source_obj = kwargs.get("page") or kwargs.get("source")

        if not source_obj or not isinstance(source_obj, (Page, Locator)):
            logger.error(
                "No Page or Locator object found in function arguments. The decorated function must have a 'page' or 'source' parameter or receive a Page/Locator object as an argument."
            )
            raise ValueError(
                "No Page or Locator object found in function arguments. The decorated function must have a 'page' or 'source' parameter or receive a Page/Locator object as an argument."
            )

        async def func_with_args():
            return await func(*args, **kwargs)

        return await _wait_for_dom_settled_core(
            source=source_obj,
            func=func_with_args,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    return wrapper


async def _wait_for_dom_settled_core(
    *,
    source: Union[Page, Locator],
    func: Callable[..., Awaitable[Any]],
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
):
    """Core function that executes the provided function and then waits for DOM to settle."""
    if not isinstance(source, (Page, Locator)):
        raise ValueError(
            "No Page or Locator object found in function arguments. Source parameter must be a Playwright Page or Locator object."
        )

    logger.debug(f"Source object: {source}")

    # Execute the function first
    result = await func()

    # Then wait for DOM to settle
    await _wait_for_dom_settled_original(
        source=source,
        settle_duration=settle_duration,
        timeout_s=timeout_s,
    )

    return result


async def _wait_for_dom_settled_original(
    source: Union[Page, Locator],
    *,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> bool:
    """Original DOM settlement detection logic."""
    if not isinstance(source, (Page, Locator)):
        raise ValueError(
            "No Page or Locator object found in function arguments. Source parameter must be a Playwright Page or Locator object."
        )

    settle_duration_ms = int(settle_duration * 1000)
    timeout_ms = int(timeout_s * 1000)

    js_code = f"""
    (target) => {{
        return new Promise((resolve, reject) => {{
            if (!target) {{
                reject(new Error('Target element not found'));
                return;
            }}

            let mutationTimer;
            let timeoutTimer;
            let settled = false;

            const observer = new MutationObserver(() => {{
                if (settled) return;

                clearTimeout(mutationTimer);
                mutationTimer = setTimeout(() => {{
                    settled = true;
                    observer.disconnect();
                    clearTimeout(timeoutTimer);
                    resolve(true);
                }}, {settle_duration_ms});
            }});

            timeoutTimer = setTimeout(() => {{
                settled = true;
                observer.disconnect();
                clearTimeout(mutationTimer);
                reject(new Error('DOM timed out settling after {timeout_ms} ms'));
            }}, {timeout_ms});

            observer.observe(target, {{
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            }});

            // Initial timer for already-stable DOM
            mutationTimer = setTimeout(() => {{
                settled = true;
                observer.disconnect();
                clearTimeout(timeoutTimer);
                resolve(true);
            }}, {settle_duration_ms});
        }});
    }}
    """

    # Get the page object
    if isinstance(source, Locator):
        frame = await get_container_frame(source)
        element_handle = await source.element_handle()
    else:
        frame = source.main_frame
        element_handle = await source.evaluate_handle("document.documentElement")

    try:
        # First, check the main frame/locator
        result = await frame.evaluate(js_code, element_handle)
        if not result:
            return False

        # Then check all nested iframes
        all_iframes = await find_all_iframes_list(frame)
        has_restricted_iframes = False
        for iframe_node in all_iframes:
            if iframe_node.allows_async_scripts:
                iframe_element_handle = await iframe_node.frame.evaluate_handle("document.documentElement")
                result = await iframe_node.frame.evaluate(js_code, iframe_element_handle)
                if not result:
                    return False
            else:
                has_restricted_iframes = True

        if has_restricted_iframes:
            logger.debug(f"Waiting {2 * settle_duration}s for iframe(s) that do not allow async scripts to settle")
            await asyncio.sleep(2 * settle_duration)

        return True
    except Exception as e:
        logger.warning(f"DOM settlement detection failed: {e}")
        return False
