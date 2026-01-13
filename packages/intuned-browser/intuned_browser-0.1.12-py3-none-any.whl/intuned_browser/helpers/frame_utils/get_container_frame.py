from playwright.async_api import ElementHandle
from playwright.async_api import Frame
from playwright.async_api import Locator


async def get_container_frame(element: Locator | ElementHandle) -> Frame:
    if isinstance(element, Locator):
        element = await element.element_handle()

    frame = await element.owner_frame()
    if not frame:
        raise ValueError("Could not get owner frame for element")

    return frame
