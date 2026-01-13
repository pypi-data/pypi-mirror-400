import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from typing import TYPE_CHECKING

from pydantic import BaseModel
from typing_extensions import override

from intuned_browser.helpers.utils.get_mode import is_generate_code_mode
from intuned_browser.helpers.utils.get_s3_client import get_async_s3_session

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class UploadedFile:
    file_name: str
    bucket: str
    region: str
    endpoint: Optional[str]
    suggested_file_name: str


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


class AttachmentType(str, Enum):
    """
    Union type representing the supported attachment file types.

    Currently supported types:
    - `"document"`: Document files (PDFs, Word docs, etc.)
    """

    DOCUMENT = "document"


class Attachment(BaseModel):
    """
    Represents an uploaded file stored in AWS S3 with metadata and utility methods.

    Provides a structured way to handle file information for files stored in S3, including methods for generating presigned URLs, serialization, and accessing file metadata.

    Attributes:
        file_name (str): The name of the file in the S3 bucket
        key (str): The key of the file in the S3 bucket
        bucket (str): The S3 bucket name where the file is stored
        region (str): The AWS region where the S3 bucket is located
        endpoint (str | None): Optional custom S3 endpoint URL. Defaults to None for standard AWS S3
        suggested_file_name (str): A human-readable filename suggestion for downloads or display
        file_type (AttachmentType): The type of the file

    Methods:
        __json__() -> dict:
            Returns a JSON-serializable dictionary representation of the file.

            Returns:
                dict: Complete model data including all fields

        to_dict() -> dict[str, str]:
            Converts the file metadata to a dictionary.

            Returns:
                dict[str, str]: Dictionary with file_name, key, bucket, region, endpoint, suggested_file_name, and file_type

        from_dict(data: dict[str, str]) -> Attachment:
            Class method to create an Attachment instance from a dictionary.

            Args:
                data (dict[str, str]): Dictionary containing file metadata

            Returns:
                Attachment: New instance created from the dictionary data

        async get_signed_url(expiration: int = 432000) -> str:
            Generates a presigned URL for secure, temporary access to the file.

            Args:
                expiration (optional[int]): URL expiration time in seconds. Defaults to 432000 (5 days)

            Returns:
                str: Presigned URL for downloading the file

        get_s3_key() -> str:
            Returns the full S3 URL for the file.

            Returns:
                str: Complete S3 URL in format: https://bucket.s3.region.amazonaws.com/filename

        get_file_path() -> str:
            Returns the file path/key within the S3 bucket.

            Returns:
                str: The file_name attribute (S3 object key)

    Examples:
        ```python Basic Usage
        from intuned_browser import upload_file_to_s3, Attachment
        async def automation(page, params, **_kwargs):
            uploaded_file: Attachment = await upload_file_to_s3(
                file=my_file,
                configs=s3_config
            )

            # Access file properties
            print(uploaded_file.file_name)
            print(uploaded_file.suggested_file_name)
        ```

        ```python Working with Presigned URLs
        from intuned_browser import upload_file_to_s3, Attachment
        async def automation(page, params, **_kwargs):
            uploaded_file: Attachment = await upload_file_to_s3(file=my_file)

            # Generate a presigned URL for temporary access
            download_url = await uploaded_file.get_signed_url(expiration=3600)  # 1 hour expiration

            # Get the permanent S3 URL
            s3_url = uploaded_file.get_s3_key()
        ```

        ```python Serialization
        from intuned_browser import upload_file_to_s3, Attachment
        async def automation(page, params, **_kwargs):
            uploaded_file: Attachment = await upload_file_to_s3(file=my_file)

            # Convert to dictionary for storage or API responses
            file_dict = uploaded_file.to_dict()
            file_json = uploaded_file.__json__()
        ```
    """

    file_name: str
    bucket: str
    region: str
    key: str
    endpoint: Optional[str] = None
    suggested_file_name: str
    file_type: AttachmentType = AttachmentType.DOCUMENT

    def __json__(self):
        return self.model_dump()

    def to_dict(self) -> dict[str, str]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Attachment":
        return cls.model_validate(data)

    async def get_signed_url(self, expiration: int = 3600 * 24 * 5) -> str:
        """
        Generate a presigned URL for downloading the file from S3.

        Args:
            expiration: URL expiration time in seconds (default: 5 days)

        Returns:
            Presigned URL string
        """
        if is_generate_code_mode():
            return "https://not.real.com"

        session, endpoint_url = get_async_s3_session(endpoint_url=self.endpoint)

        async with session.client("s3", endpoint_url=endpoint_url) as s3_client:
            response = await s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket, "Key": self.file_name},
                ExpiresIn=expiration,
                HttpMethod="GET",
            )
        return response

    def get_s3_key(self):
        if isinstance(self.endpoint, str) and self.endpoint != "":
            raise ValueError(
                "get_s3_key function is not supported when using a custom s3 endpoint, please use get_signed_url instead"
            )
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{self.file_name}"

    def get_file_path(self):
        return self.file_name


class SignedUrlAttachment(Attachment):
    _download_signed_url: str

    def __init__(
        self,
        *,
        file_name: str,
        download_signed_url: str,
        suggested_file_name: str,
    ):
        super().__init__(
            file_name=file_name,
            key=file_name,
            bucket="",
            region="",
            endpoint=None,
            suggested_file_name=suggested_file_name,
            file_type=AttachmentType.DOCUMENT,
        )
        self._download_signed_url = download_signed_url

    @override
    async def get_signed_url(self, expiration: Optional[int] = 3600 * 24 * 5) -> str:
        """Return the pre-signed download URL (already signed, so expiration is ignored)."""
        return self._download_signed_url

    @override
    def get_s3_key(self):
        raise Exception("SignedUrlAttachment does not support get_s3_key function")
