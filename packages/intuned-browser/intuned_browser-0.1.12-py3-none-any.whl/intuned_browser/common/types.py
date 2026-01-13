from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class RunningEnvironment(Enum):
    AUTHORING = "AUTHORING"
    PUBLISHED = "PUBLISHED"
    UNDEFINED = "UNDEFINED"


class S3Configs(BaseModel):
    """
    Configuration class for AWS S3 storage operations.

    This class defines the configuration parameters needed to connect to and interact
    with AWS S3 storage services. It supports both standard AWS S3 and S3-compatible
    storage services through custom endpoints.

    Attributes:
        access_key (str | None): AWS access key ID for authentication. If None, will attempt to use default AWS credentials or environment variables.
        secret_key (str | None): AWS secret access key for authentication. If None, will attempt to use default AWS credentials or environment variables.
        bucket_name (str | None): Name of the S3 bucket to store files in. Must be a valid S3 bucket name following AWS naming conventions.
        region (str | None): AWS region where the S3 bucket is located. Examples: 'us-east-1', 'eu-west-1', 'ap-southeast-1'
        endpoint (str | None): Custom endpoint URL for S3-compatible storage services. Use this for services like MinIO, DigitalOcean Spaces, or other S3-compatible APIs. For standard AWS S3, leave this as None.

    Examples:
        ```python Basic Configuration
        from intuned_browser import S3Configs
        async def automation(page, params, **_kwargs):
            # Using explicit credentials
            s3_config = S3Configs(
                access_key="accessKeyId",
                secret_key="SecretAccessKeyId",
                bucket_name="my-app-uploads",
                region="us-east-1"
            )
        ```

        ```python Environment Variables Configuration
        from intuned_browser import S3Configs
        async def automation(page, params, **_kwargs):
            # Credentials will be picked up from environment or IAM roles
            s3_config = S3Configs(
                bucket_name="my-app-uploads",
                region="us-west-2"
            )
        ```
    """

    access_key: str | None = Field(
        description="AWS access key ID for authentication. If None, will attempt to use default AWS credentials or environment variables.",
        default=None,
    )
    secret_key: str | None = Field(
        description="AWS secret access key for authentication. If None, will attempt to use default AWS credentials or environment variables.",
        default=None,
    )
    bucket_name: str | None = Field(
        description="Name of the S3 bucket to store files in. Must be a valid S3 bucket name following AWS naming conventions.",
        default=None,
    )
    region: str | None = Field(
        description="AWS region where the S3 bucket is located. Examples: 'us-east-1', 'eu-west-1', 'ap-southeast-1'",
        default=None,
    )
    endpoint: str | None = Field(
        description="Custom endpoint URL for S3-compatible storage services. Use this for services like MinIO, DigitalOcean Spaces, or other S3-compatible APIs. For standard AWS S3, leave this as None.",
        default=None,
    )
