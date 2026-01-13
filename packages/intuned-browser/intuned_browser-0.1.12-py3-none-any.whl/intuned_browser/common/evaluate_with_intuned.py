from pathlib import Path
from typing import Any
from typing import Union

from playwright.async_api import Locator
from playwright.async_api import Page


async def evaluate_with_intuned(
    source: Union[Page, Locator],
    script: str,
    arg: Any = None,
) -> Any:
    browser_scripts_path = Path(__file__).parent / "browser_scripts.js"
    browser_scripts_content = browser_scripts_path.read_text()
    combined_script = f"""
    (arg) => {{
        if (typeof window.__INTUNED__ === "undefined") {{
            {browser_scripts_content}
        }}
        const userFunction = {script};
        return userFunction(arg);
    }}
    """

    return await source.evaluate(combined_script, arg)
