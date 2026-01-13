from _typeshed import Incomplete

logger: Incomplete

def get_file_from_gdrive(gdrive_source: str) -> bytes | None:
    """Download a file from Google Drive given a file ID or URL.

    Args:
        gdrive_source (str): Google Drive file ID or full URL.

    Returns:
        bytes | None: The file's binary content if successful, None otherwise.
    """
