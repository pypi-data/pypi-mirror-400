import logging
import os
import re
import uuid
from typing import Any
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

import aiofiles
import httpx
from botocore.exceptions import NoCredentialsError
from playwright.async_api import Download
from pydantic import BaseModel
from pydantic import Field

from intuned_browser.helpers.types import AttachmentType

if TYPE_CHECKING:
    pass

try:
    from runtime.backend_functions._call_backend_function import call_backend_function
except ImportError:
    call_backend_function = None
    import logging

    logging.warning(
        "Runtime dependencies are not available. Uploading file without S3 credentials will not be available. Install 'intuned-runtime' to enable this feature."
    )

from intuned_browser.helpers.types import Attachment
from intuned_browser.helpers.types import S3Configs
from intuned_browser.helpers.types import SignedUrlAttachment
from intuned_browser.helpers.utils.get_mode import is_generate_code_mode
from intuned_browser.helpers.utils.get_s3_client import get_async_s3_session

logger = logging.getLogger(__name__)


type FileType = Download | bytes
"""
A union type representing supported file types for upload operations in web automation.

This type alias standardizes the file types that can be uploaded to S3 storage,
providing flexibility for different upload scenarios from browser downloads to raw binary data.

Type variants:
    - `Download`: Playwright Download object from browser download operations
    - `bytes`: Raw binary file content

Examples:
    ```python Using Download Object
    from typing import TypedDict
    from playwright.async_api import Page
    from intuned_browser import download_file, upload_file_to_s3
    class Params(TypedDict):
        pass
    async def automation(page: Page, params: Params, **_kwargs):
        # From a browser download
        download = await download_file(
            page,
            trigger="https://intuned-docs-public-images.s3.amazonaws.com/32UP83A_ENG_US.pdf"
        )
        uploaded = await upload_file_to_s3(file=download)
    ```

    ```python Using Bytes
    from typing import TypedDict
    from playwright.async_api import Page
    from intuned_browser import upload_file_to_s3
    class Params(TypedDict):
        pass
    async def automation(page: Page, params: Params, **_kwargs):
        # From raw bytes
        file_buffer = b"PDF content here..."
        uploaded = await upload_file_to_s3(
            file=file_buffer,
            file_name_override="generated.pdf"
        )
    ```
"""


def _normalize_s3_config(configs: Union[S3Configs, dict[str, Any], None]) -> Optional[S3Configs]:
    """
    Convert dict to S3Configs or return None if configs is None.
    Raises TypeError if configs is neither None, dict, nor S3Configs.
    """
    if configs is None:
        return None

    if isinstance(configs, S3Configs):
        return configs

    if isinstance(configs, dict):
        try:
            return S3Configs(**configs)
        except Exception as e:
            raise ValueError("Invalid S3 configuration dict") from e

    raise TypeError(f"configs must be S3Configs, dict, or None. Got: {type(configs)}")


def sanitize_key(key):
    """
    Sanitize a key string by replacing non-alphanumeric characters with underscores
    and consolidating multiple underscores into single underscores.
    Args:
        key (str): The input string to sanitize
    Returns:
        str: Sanitized string
    """
    # Replace any non-alphanumeric chars (except .-_/) with underscore
    result = re.sub(r"[^a-zA-Z0-9.\-_/]", "_", key)
    # Replace multiple underscores with single underscore
    result = re.sub(r"_{2,}", "_", result)
    return result


async def upload_file_to_s3(
    file: FileType,
    *,
    configs: S3Configs | None = None,
    file_name_override: str | None = None,
    content_type: str | None = None,
) -> Attachment:
    """
    Uploads files to AWS S3 storage with flexible configuration options.

    This function accepts various file types including Playwright Download objects, binary data,
    making it versatile for different upload scenarios. It automatically handles file metadata
    and provides comprehensive S3 configuration options.

    ## S3 configuration fallback

    The function uses a fallback system to determine S3 settings:

    1. **S3Configs Parameter** - If provided, uses the explicit `S3Configs` object with your custom settings.
    2. **Environment Variables** - If no configs provided, automatically reads from environment variables:
       - `AWS_ACCESS_KEY_ID` - Your AWS access key
       - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
       - `AWS_REGION` - AWS region (e.g., "us-west-1")
       - `AWS_BUCKET` - S3 bucket name
       - `AWS_ENDPOINT_URL` - Optional custom S3 endpoint
       - Check [Environment Variables & Secrets](https://docs.intunedhq.com/docs/02-features/environment-variables-secrets) to learn more about setting environment variables.
    3. **Intuned Defaults** - If environment variables aren't set, falls back to Intuned's managed S3 storage. See [S3 Attachment Storage](https://docs.intunedhq.com/docs/04-integrations/s3/s3-attachment-storage) for more details.

    Args:
        file (FileType): The file to upload. See [FileType](../type-references/FileType) for supported types.
        configs (optional[S3Configs]): Optional [S3Configs](../type-references/S3Configs) for customizing the S3 upload. If not provided, uses environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_ENDPOINT_URL`, `AWS_BUCKET`). If environment variables aren't set, uses default Intuned S3 settings.
        file_name_override (optional[str]): Optional custom filename for the uploaded file. If not provided, uses the original filename or generates a unique name.
        content_type (optional[str]): Optional MIME type for the uploaded file (e.g., "application/pdf", "image/png"). If None, uses the original content type.

    Returns:
        Attachment: An [Attachment](../type-references/Attachment) object with file metadata and utility methods

    Examples:
        ```python Upload Downloaded File
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import download_file, upload_file_to_s3
        from intuned_browser import S3Configs
        import os
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto("https://sandbox.intuned.dev/pdfs")
            download = await download_file(
                page,
                trigger=page.locator("xpath=//tbody/tr[1]//*[name()='svg']")
            )
            # Set your environment variables for the AWS credentials.
            # Check https://docs.intunedhq.com/docs/02-features/environment-variables-secrets to learn more about setting environment variables.
            uploaded_file = await upload_file_to_s3(
                file=download,
                configs=S3Configs(
                    bucket_name=os.environ['AWS_BUCKET'],
                    region=os.environ['AWS_REGION'],
                    access_key=os.environ['AWS_ACCESS_KEY_ID'],
                    secret_key=os.environ['AWS_SECRET_ACCESS_KEY']
                ),
                file_name_override='reports/monthly-report.pdf'
            )

            print(f"File uploaded: {uploaded_file.suggested_file_name}")
        ```

        ```python Upload Binary Data
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser import upload_file_to_s3
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            file_buffer = b'Hello World'
            uploaded_file = await upload_file_to_s3(
                file=file_buffer,
                file_name_override='data/text-file.txt',
                content_type='text/plain'
            )

            # Generate a temporary download URL
            download_url = await uploaded_file.get_signed_url()
            print(f"Download URL: {download_url}")
            return {
                'download_url': download_url
            }
        ```
    """
    if not isinstance(file, (Download, bytes)):
        raise ValueError("Invalid file type, Supported types are Download and bytes")
    if configs is None:
        configs = S3Configs()
    configs = _normalize_s3_config(configs)
    bucket_name = (
        configs.bucket_name
        if (configs and configs.bucket_name)
        else (os.environ.get("AWS_BUCKET") or os.environ.get("INTUNED_S3_BUCKET"))
    )
    region = (
        configs.region
        if (configs and configs.region)
        else (os.environ.get("AWS_REGION") or os.environ.get("INTUNED_S3_REGION"))
    )
    endpoint = (
        configs.endpoint
        if (configs and configs.endpoint)
        else (os.environ.get("AWS_ENDPOINT_URL") or os.environ.get("INTUNED_S3_ENDPOINT_URL"))
    )

    is_downloaded_file = isinstance(file, Download)
    if is_generate_code_mode():
        logger.info("Uploaded file successfully")
        if is_downloaded_file:
            return Attachment(
                file_name=f"{str(uuid.uuid4())}/{file.suggested_filename}",
                bucket="testing_bucket",
                region="testing_region",
                endpoint=endpoint,
                suggested_file_name=file.suggested_filename,
                file_type=AttachmentType.DOCUMENT,
                key=f"{str(uuid.uuid4())}/{file.suggested_filename}",
            )
        else:
            suggested_file_name = str(uuid.uuid4())
            return Attachment(
                file_name=suggested_file_name,
                bucket="testing_bucket",
                region="testing_region",
                endpoint=endpoint,
                suggested_file_name=suggested_file_name,
                file_type=AttachmentType.DOCUMENT,
                key=suggested_file_name,
            )

    suggested_file_name = file.suggested_filename if is_downloaded_file else None
    logger.info(f"suggested_file_name {suggested_file_name}")
    file_name = file_name_override if file_name_override is not None else suggested_file_name or str(uuid.uuid4())

    file_body = await get_file_body(file)

    if region is None or bucket_name is None:
        return await upload_to_intuned(
            name=file_name,
            suggested_name=suggested_file_name,
            body=file_body,
        )

    if is_downloaded_file and not await file.path():
        raise ValueError("File path not found")

    session, endpoint_url = get_async_s3_session(endpoint, configs)

    cleaned_file_name = sanitize_key(file_name)
    key = f"{uuid.uuid4()}/{cleaned_file_name}"
    try:
        async with session.client("s3", endpoint_url=endpoint_url) as s3_client:
            if content_type:
                response = await s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=file_body,
                    ContentType=content_type,
                )
            else:
                response = await s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=file_body,
                )

    except NoCredentialsError:
        raise Exception("Credentials not available")  # noqa: B904
    finally:
        if isinstance(file, Download):
            await file.delete()

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return Attachment(
            file_name=key,
            key=key,
            bucket=bucket_name,
            region=region,
            endpoint=endpoint,
            suggested_file_name=suggested_file_name or "",
            file_type=AttachmentType.DOCUMENT,
        )
    else:
        raise Exception("Error uploading file")


async def get_file_body(file: Download | bytes):
    if isinstance(file, Download):
        file_path = await file.path()
        if not file_path:
            raise ValueError("Downloaded file path not found")
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
    elif isinstance(file, bytes):
        return file
    else:
        raise ValueError("Invalid file type")


class GetUploadSignedUrlResponse(BaseModel):
    id: str
    write_signed_url: str = Field(alias="writeSignedUrl")
    read_signed_url: str = Field(alias="readSignedUrl")


async def upload_to_intuned(
    *,
    name: str,
    suggested_name: Optional[str],
    body: bytes,
):
    if call_backend_function is None:
        raise Exception(
            "Runtime dependencies are not available. Uploading file without S3 credentials will not be available."
        )
    response = await call_backend_function(
        name="files/uploadSignedUrls",
        validation_model=GetUploadSignedUrlResponse,
        method="GET",
    )
    async with httpx.AsyncClient() as client:
        put_response = await client.put(
            response.write_signed_url,
            data=body,  # type: ignore
        )
        if not (200 <= put_response.status_code < 300):
            raise Exception(f"Error uploading file: {put_response.status_code} {put_response.text}")
    return SignedUrlAttachment(
        file_name=name,
        download_signed_url=response.read_signed_url,
        suggested_file_name=suggested_name or name,
    )
