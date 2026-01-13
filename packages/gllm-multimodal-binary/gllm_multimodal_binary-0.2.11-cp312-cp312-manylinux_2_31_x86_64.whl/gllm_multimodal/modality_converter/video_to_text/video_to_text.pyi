from abc import ABC, abstractmethod
from gllm_multimodal.modality_converter.modality_converter import BaseModalityConverter as BaseModalityConverter
from gllm_multimodal.modality_converter.schema.text_result import TextResult as TextResult
from typing import Any

class BaseVideoToText(BaseModalityConverter, ABC):
    """Abstract base class for video-to-text conversion."""
    async def convert(self, source: str | bytes, **kwargs: Any) -> TextResult:
        """Executes the video to text process.

        This method validates the input parameters and calls `_convert` to perform the video to text process.
        It ensures that the required source parameter is provided and valid before proceeding.

        Args:
            source (str | bytes): The source of the video to convert to text.
            **kwargs (Any): A dictionary of arguments required for the video to text process.
                Must include `source` of type `str`.
                May include additional parameters specific to the implementation.

        Returns:
            TextResult: The result of processing the video.

        Raises:
            ValueError: If `source` is missing from the input kwargs or is empty.
            TypeError: If `source` is not a string or bytes.
        """
    @classmethod
    @abstractmethod
    def from_preset(cls, preset_name: str | None = 'default', **kwargs: Any) -> BaseVideoToText:
        '''Initialize the video to text converter using preset model configurations.

        This abstract classmethod must be implemented by subclasses to define how to create
        an instance from a preset configuration.

        Args:
            preset_name (str | None): Name of the preset to use. Defaults to "default".
            **kwargs (Any): Additional keyword arguments to pass to the preset configuration.

        Returns:
            BaseVideoToText: Initialized video to text converter using preset model.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        '''
