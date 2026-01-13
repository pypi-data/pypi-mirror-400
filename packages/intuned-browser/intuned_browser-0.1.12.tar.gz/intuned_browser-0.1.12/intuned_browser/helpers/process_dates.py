from datetime import datetime

from dateutil import parser


def process_date(date_string: str) -> datetime | None:
    """
    Parses various date string formats into datetime objects, returning only the date part with time set to midnight.
    This utility function provides robust date parsing capabilities for a wide range of common formats.

    ## Key features

    - Returns only the date part (year, month, day)
    - Time is always set to 00:00:00
    - Supports multiple international formats
    - Handles timezones and AM/PM formats

    ## Supported formats

    The function handles these date format categories:

    ### Standard date formats
    - `DD/MM/YYYY`: "22/11/2024", "13/12/2024"
    - `MM/DD/YYYY`: "01/17/2025", "10/25/2024"
    - Single-digit variants: "8/16/2019", "9/28/2024"

    ### Date-time combinations
    - With 24-hour time: "22/11/2024 21:19:05"
    - With AM/PM: "12/09/2024 9:00 AM"
    - With dash separator: "12/19/2024 - 2:00 PM"

    ### Timezone support
    - With timezone abbreviations: "10/23/2024 12:06 PM CST"
    - With timezone offset: "01/17/2025 3:00:00 PM CT"

    ### Text month formats
    - Short month: "5 Dec 2024", "11 Sep 2024"
    - With time: "5 Dec 2024 8:00 AM PST"
    - Full month: "November 14, 2024", "January 31, 2025, 5:00 pm"

    Args:
        date_string (str): A string containing a date in various possible formats

    Returns:
        datetime | None: Returns a `datetime` object with only date components preserved (year, month, day), time always set to 00:00:00, or `None` if parsing fails

    Examples:
        ```python Basic Usage
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import process_date
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Basic date string
            date1 = process_date("22/11/2024")
            print(date1)  # 2024-11-22 00:00:00

            # Date with time (time is ignored)
            date2 = process_date("5 Dec 2024 8:00 AM PST")
            print(date2)  # 2024-12-05 00:00:00
        ```

        ```python Invalid Date
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import process_date
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # Invalid date returns None
            invalid_date = process_date("invalid date")
            print(invalid_date)  # will return None.
            if invalid_date is None:
                raise Exception("Invalid date")
            return "should not reach here"
        ```
    """
    try:
        # Handle the case where there's a hyphen used as separator
        date_string = date_string.replace(" - ", " ")

        # Parse the date string with dayfirst=False to handle MM/DD/YYYY format
        parsed_date = parser.parse(date_string, dayfirst=False)
        return parsed_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    except (ValueError, TypeError):
        return None
