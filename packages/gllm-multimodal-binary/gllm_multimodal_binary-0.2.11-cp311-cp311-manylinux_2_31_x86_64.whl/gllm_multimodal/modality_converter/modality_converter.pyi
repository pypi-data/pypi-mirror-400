from abc import ABC, abstractmethod
from gllm_multimodal.modality_converter.schema.text_result import TextResult as TextResult
from typing import Any

class BaseModalityConverter(ABC):
    """An abstract base class for modality conversion used in Gen AI applications.

    This class provides a foundation for building modality converter components in Gen AI applications.
    It supports converting between different modalities (e.g. text, images, audio, video) and can be extended
    to implement various types of conversion tasks like OCR, captioning, speech-to-text, text-to-speech, etc.
    """
    def __init__(self) -> None:
        """Initialize the base modality converter component with logging capabilities."""
    @abstractmethod
    async def convert(self, source: str | bytes, **kwargs: Any) -> TextResult:
        """Executes the modality conversion process.

        This method validates the input parameters and calls `convert` to perform the modality conversion process.
        It ensures that the required source parameter is provided and valid before proceeding.

        Args:
            source (str | bytes): The source of the modality to convert.
            **kwargs (Any): A dictionary of arguments required for the modality conversion process.
                Must include `source` of type `str`.
                May include additional parameters specific to the implementation.

        Returns:
            TextResult: The result of processing the modality.

        Raises:
            ValueError: If `source` is missing from the input kwargs or is empty.
            TypeError: If `source` is not a string or bytes.
            NotImplementedError: If the method is not implemented in a subclass.
        """
