import logging

from playwright.async_api import Page

from intuned_browser.helpers.download_file import download_file
from intuned_browser.helpers.download_file import Trigger
from intuned_browser.helpers.types import Attachment
from intuned_browser.helpers.types import S3Configs
from intuned_browser.helpers.upload_file import upload_file_to_s3
from intuned_browser.helpers.utils.get_mode import is_generate_code_mode

logger = logging.getLogger(__name__)


async def save_file_to_s3(
    page: Page,
    trigger: Trigger,
    *,
    timeout_s: int = 5,
    configs: S3Configs | None = None,
    file_name_override: str | None = None,
    content_type: str | None = None,
) -> Attachment:
    """
    Downloads a file from a web page and automatically uploads it to AWS S3 storage in a single operation.

    Combines [download_file](./download_file) (for trigger methods) and [upload_file_to_s3](./upload_file_to_s3)
    (for S3 configuration), providing a streamlined workflow for capturing and storing files.

    Args:
        page (Page): The Playwright Page object to use for downloading
        trigger (Trigger): The [Trigger](../type-references/Trigger) method to initiate the download.
        timeout_s (optional[int]): Maximum time in seconds to wait for download to start. Defaults to 5.
        configs (optional[S3Configs]): Optional [S3Configs](../type-references/S3Configs) to customize the S3 upload. If not provided, uses environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_ENDPOINT_URL`, `AWS_BUCKET`). If environment variables aren't set, uses default Intuned S3 settings.
        file_name_override (optional[str]): Optional custom filename for the uploaded file. If not provided, uses the original filename or generates a unique name.
        content_type (optional[str]): Optional MIME type for the uploaded file (e.g., "application/pdf", "image/png"). If None, uses the original content type.

    Returns:
        Attachment: An [Attachment](../type-references/Attachment) object with file metadata and S3 utilities

    Examples:
        ```python URL Trigger
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import save_file_to_s3, S3Configs
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            uploaded_file = await save_file_to_s3(
                page=page,
                trigger="https://sandbox.intuned.dev/pdfs/report.pdf",
                configs=S3Configs(
                    bucket_name='document-storage',
                    region='us-east-1',
                    access_key='accessKeyId',
                    secret_key='SecretAccessKeyId'
                ),
                file_name_override='reports/monthly-report.pdf'
            )
            print(f"File uploaded to: {uploaded_file.get_s3_key()}")
        ```

        ```python Locator Trigger
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import save_file_to_s3
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/pdfs")
            uploaded_file = await save_file_to_s3(
                page=page,
                trigger=page.locator("xpath=//tbody/tr[1]//*[name()='svg']"),
                timeout_s=10
            )
            download_url = await uploaded_file.get_signed_url(7200)  # 2 hours
            print(f"Temporary access: {download_url}")
        ```
    """
    if not isinstance(page, Page):
        raise ValueError("page must be a playwright Page object")
    download = await download_file(page, trigger, timeout_s=timeout_s)
    if not is_generate_code_mode():
        try:
            from intuned_runtime import extend_timeout

            extend_timeout()
        except ImportError:
            logger.info(
                "Intuned Runtime not available: extend_timeout() was not called. Install 'intuned-runtime' to enable this feature."
            )
    attachment: Attachment = await upload_file_to_s3(
        download, configs=configs, file_name_override=file_name_override, content_type=content_type
    )
    return attachment
