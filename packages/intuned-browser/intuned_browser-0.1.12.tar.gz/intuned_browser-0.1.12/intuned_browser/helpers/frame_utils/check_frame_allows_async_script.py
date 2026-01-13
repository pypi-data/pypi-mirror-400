import logging

from playwright.async_api import ElementHandle

logger = logging.getLogger(__name__)


async def check_frame_allows_async_scripts(iframe_element: ElementHandle) -> bool:
    """
    Check if an iframe element allows asynchronous script operations.

    - Synchronous code execution (e.g., via frame.evaluate()) still works
    - Asynchronous operations do not work, including:
      * Event listeners (addEventListener)
      * Callbacks (setTimeout, setInterval)
      * Promise-based operations
      * Async/await code

    Currently, the only known case where this is False is when the iframe has a sandbox attribute without 'allow-scripts'.
    """
    try:
        sandbox_value = await iframe_element.evaluate("(element) => element.getAttribute('sandbox')")
        if sandbox_value is None:
            return True

        sandbox_tokens = sandbox_value.strip().split()
        return "allow-scripts" in sandbox_tokens
    except Exception as e:
        logger.warning(f"Error checking iframe sandbox attribute: {e}", exc_info=False)
        return True
