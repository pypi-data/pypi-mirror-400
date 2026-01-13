from abc import ABC
from gllm_multimodal.modality_converter.modality_converter import BaseModalityConverter as BaseModalityConverter
from gllm_multimodal.modality_converter.schema.text_result import TextResult as TextResult
from gllm_multimodal.utils.image_utils import get_image_binary as get_image_binary
from typing import Any

class BaseImageToText(BaseModalityConverter, ABC):
    """An abstract base class for image to text conversion used in Gen AI applications.

    This class provides a foundation for building image to text converter components in Gen AI applications.
    It supports various types of image sources (file paths, URLs, base64 strings) and can be extended
    to implement different types of image analysis tasks like OCR, captioning, or object detection.
    """
    def __init__(self) -> None:
        """Initialize the base image to text component with logging capabilities."""
    async def convert(self, source: str | bytes, **kwargs: Any) -> TextResult:
        """Executes the image to text process.

        This method validates the input parameters and calls `convert` to perform the image to text process.
        It ensures that the required image_source parameter is provided and valid before proceeding.

        Args:
            source (str | bytes): The source of the image to convert to text.
            **kwargs (Any): A dictionary of arguments required for the image to text process.
                Must include `source` of type `str`.
                May include additional parameters specific to the implementation.

        Returns:
            ImageToTextResult: The result of processing the image.

        Raises:
            ValueError: If `source` is missing from the input kwargs or is empty.
            TypeError: If `source` is not a string or bytes.
        """
