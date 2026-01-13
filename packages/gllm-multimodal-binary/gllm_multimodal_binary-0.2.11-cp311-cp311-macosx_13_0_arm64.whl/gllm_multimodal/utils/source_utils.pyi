from _typeshed import Incomplete
from aiohttp import ClientSession

logger: Incomplete

async def get_file_from_url(file_source: str, timeout: int = 30, session: ClientSession | None = None) -> bytes | None:
    """Asynchronously download and validate an image from a URL.

    This function performs the following steps:
    1. Attempts to download the content from the provided URL.
    2. Validates that the downloaded content is a valid image.
    3. Returns the binary data if both steps succeed.

    Args:
        file_source (str): The URL of the file to download.
            Supports HTTP and HTTPS protocols.
        timeout (int, optional): The timeout for the HTTP request in seconds.
            Defaults to 30 seconds.
        session (Optional[aiohttp.ClientSession], optional): An existing aiohttp session to use.
            If None, a new session will be created. Defaults to None.

    Returns:
        bytes | None: The downloaded image binary data if successful and valid,
            None if the download fails or the content is not a valid image.
    """
def get_file_from_file_path(source: str) -> bytes | None:
    """Read image file and return its binary data if valid.

    Args:
        source (str): Path to the image file.

    Returns:
        bytes | None: Binary data of the image file if valid, None otherwise.
    """
def encode_file_to_base64(file_binary: bytes) -> str:
    """Convert binary file data to base64 string.

    Args:
        file_binary (bytes): Binary data of the file.

    Returns:
        str: Base64 encoded string.
    """
