from _typeshed import Incomplete
from gllm_multimodal.constants import ExifConstants as ExifConstants
from typing import Any

logger: Incomplete
semantic_router_logger: Incomplete

def get_image_metadata(image_binary: bytes) -> dict[str, Any]:
    """Extract metadata from image binary data.

    This function extracts metadata from the image, including:
    1. GPS coordinates (latitude/longitude) if available in EXIF data

    Args:
        image_binary (bytes): The binary data of the image.

    Returns:
        dict[str, Any]: Dictionary containing image metadata.
    """
