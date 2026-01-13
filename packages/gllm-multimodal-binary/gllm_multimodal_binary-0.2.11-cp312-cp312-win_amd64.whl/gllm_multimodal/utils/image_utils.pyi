from _typeshed import Incomplete
from gllm_multimodal.constants import ImageToTextConstants as ImageToTextConstants
from gllm_multimodal.utils.gdrive_utils import get_file_from_gdrive as get_file_from_gdrive
from gllm_multimodal.utils.s3_utils import get_file_from_s3 as get_file_from_s3
from gllm_multimodal.utils.source_utils import get_file_from_file_path as get_file_from_file_path, get_file_from_url as get_file_from_url
from typing import Any

logger: Incomplete

def is_binary_image(image_binary_data: bytes) -> bool:
    """Validate if the provided binary data represents a valid image file.

    This function attempts to open the binary data as an image using PIL (Python Imaging Library)
    to verify if it represents a valid image format.

    Args:
        image_binary_data (bytes): The binary data to validate.

    Returns:
        bool: True if the binary data represents a valid image that can be opened by PIL,
            False otherwise.
    """
def get_image_from_base64(image_source: str) -> bytes | None:
    """Decode and validate a base64 encoded image string.

    This function attempts to:
    1. Decode the provided base64 string
    2. Validate that the decoded data represents a valid image
    3. Return the binary data if both steps succeed

    Args:
        image_source (str): The base64 encoded image string to decode.
            Should be a valid base64 string without the data URI prefix
            (e.g., without 'data:image/jpeg;base64,').

    Returns:
        bytes | None: The decoded image binary data if successful and valid,
            None if either the decoding fails or the data is not a valid image.

    Note:
        1. The function performs validation using is_binary_image()
        2. Invalid base64 strings or non-image data will return None
        3. Logs debug messages on failure for troubleshooting
    """
async def get_image_binary(image_source: Any) -> tuple[bytes | None, str | None]:
    """Retrieve image binary data from various sources.

    This function acts as a unified interface for retrieving image data from different sources:
    1. Local file paths
    2. URLs (HTTP/HTTPS)
    3. Base64 encoded strings
    4. S3 URLs (s3:// or https://)

    The function automatically detects the source type and uses the appropriate method
    to retrieve the image data.

    Args:
        image_source (Any): The source of the image, which can be:
            1. bytes: Direct binary data
            2. str: Base64 string, file path, URL, or S3 URL

    Returns:
        tuple[bytes | None, str | None]: A tuple containing:
            1. The image binary data if successful, None if failed
            2. The filename if available, None for direct binary or base64
    """
def get_unique_non_empty_strings(texts: list[str]) -> list[str]:
    """Get unique non-empty strings from a list of strings and remove whitespace.

    This function takes a list of strings and returns a list of strings where each
    string from the list is not empty or whitespace-only. It also removes duplicates.

    Args:
        texts (list[str]): A list of strings to combine.

    Returns:
        list[str]: A list of strings where each string is not empty or whitespace-only.
    """
def combine_strings(texts: list[str]) -> str:
    """Combine multiple strings into a single string with newline separators.

    This function takes a list of strings and returns a single string where each
    string from the list is on a new line. It filters out any empty or whitespace-only
    strings from the list before joining them.

    Args:
        texts (list[str]): A list of strings to combine.

    Returns:
        str: A single string containing all valid strings, where each string is on a new line.
    """
