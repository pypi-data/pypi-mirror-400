import base64
import logging

import litellm
from playwright.async_api import Page

from intuned_browser.intuned_services.api_gateways import GatewayFactory

litellm.set_verbose = False  # type: ignore

# Suppress verbose LiteLLM logs
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def is_page_loaded(
    page: Page,
    *,
    model: str = "claude-haiku-4-5-20251001",
    timeout_s: int = 10,
    api_key: str | None = None,
) -> bool:
    """
    Uses AI vision to determine if a webpage has finished loading by analyzing a screenshot.
    Detects loading spinners, blank content, or incomplete page states.

    Args:
        page (Page): The Playwright page to check
        timeout_s (optional[int]): Screenshot timeout in seconds. Defaults to 10.
        model (optional[str]): AI model to use for the check. Defaults to "claude-haiku-4-5-20251001".
        api_key (optional[str]): Optional API key for the AI service (if provided, will not be billed to your account). Defaults to None.

    Returns:
        bool: True if page is loaded, False if still loading

    Examples:
        ```python Check Page Loading
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser.ai import is_page_loaded
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Wait for page to finish loading
            await page.goto('https://sandbox.intuned.dev/')

            page_loaded = await is_page_loaded(page)
            if page_loaded:
                # Continue with scraping or interactions
                print("Page is loaded")
            else:
                # Wait longer or retry
                await page.wait_for_timeout(5000)
        ```

        ```python Loading Loop
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser.ai import is_page_loaded
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Keep checking until page loads
            await page.goto("https://example.com")
            attempts = 0
            while attempts < 10:  # We will retry up to 10 times with a 2-second delay between attempts.
                page_loaded = await is_page_loaded(
                    page,
                    model="claude-3-7-sonnet-latest",
                    timeout_s=5
                )
                if page_loaded:
                    break  # If the page is loaded, break the loop.

                await page.wait_for_timeout(2000)  # Wait for 2 seconds before the next attempt.
                attempts += 1
        ```
    """
    gateway = GatewayFactory.create_ai_gateway(model=model, api_key=api_key)
    screenshot_bytes = await page.screenshot(full_page=False, type="png", timeout=timeout_s * 1000)

    base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
    response = await gateway.acompletion(
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that determines if a webpage finished loading. If the page finished loading, start your answer with 'True'. If the page is loading, start your answer with 'False'. If you are not sure, start your answer with 'Dont know'. In a new line, add a reason to your response.

## Some good cues for determining if a page is loading (return 'False'):
- Loading spinner
- Page is blank
- Some content looks like it's missing
- Not on splash screen


## Special cases for LOADED pages (return 'True')
- CAPTCHA challenges are considered loaded, because it is indeed loaded and waiting for the user to solve the captcha.
- Bot detection screens (e.g., "Checking your browser", Cloudflare verification) are considered loaded, because it is indeed loaded and waiting for the user to solve the captcha.
- Static error pages (404 Not Found, 403 Forbidden, 500 Internal Server Error, etc.)
- Login/authentication screens
- Complete forms ready for user input
- Fully rendered articles, product pages, or dashboards
- Cookie consent banners or popups over complete content
- Payment or checkout pages with all fields visible
""",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64," + base64_image},
                    },
                    {
                        "type": "text",
                        "text": "Look at the screenshot and tell me, is the page loading or has it finished loading?",
                    },
                ],
            },
        ],
    )

    llm_result = response.choices[0].message.content
    # Normalize multiple newlines to one
    llm_result = "\n".join(filter(None, llm_result.split("\n")))
    if llm_result is None:
        raise ValueError("LLM result is None")
    is_true = "True" in llm_result
    is_false = "False" in llm_result
    is_dont_know = "Dont know" in llm_result
    reason = llm_result.split("\n")[1] if len(llm_result.split("\n")) > 1 else None
    result: bool
    if is_true:
        result = True
    elif is_false:
        result = False
    elif is_dont_know:
        result = False
    else:
        raise ValueError("LLM result is not valid")
    if response._response_headers and response._response_headers.get("x-ai-cost-in-cents"):
        logger.info(f"Total LLM Cost In Cents: {response._response_headers['x-ai-cost-in-cents']}")
    else:
        logger.info(f"Total LLM Tokens: {response.usage.total_tokens}")
    logger.debug(f"Reason: {reason}")
    return result
