import re
from typing import Optional, Tuple
from climb_jupyter_base.exceptions import ValidationError


def validate_s3_uri(uri: Optional[str]) -> Tuple[str, str]:
    """
    Validate `uri` is a valid S3 URI and return the bucket name and key.

    S3 URIs are expected to be in the format `s3://bucket_name/key`, where:
    - `bucket_name` is the name of the S3 bucket (3-63 characters, lowercase letters, numbers, hyphens, and periods).
    - `key` is the path to the object in the bucket (can contain any characters).

    Args:
        uri: The S3 URI to validate.

    Returns:
        A tuple containing the bucket name and key.

    Raises:
        ValidationError: If the URI is invalid.
    """

    if not uri:
        raise ValidationError("S3 URI is required")

    pattern = re.compile(r"^s3:\/\/([a-z0-9.-]{3,63})\/(.+)$")
    result = pattern.match(uri)

    if not result or len(result.groups()) != 2:
        raise ValidationError(f"Invalid S3 URI: {uri}")

    bucket_name, key = result.groups()
    return bucket_name, key
