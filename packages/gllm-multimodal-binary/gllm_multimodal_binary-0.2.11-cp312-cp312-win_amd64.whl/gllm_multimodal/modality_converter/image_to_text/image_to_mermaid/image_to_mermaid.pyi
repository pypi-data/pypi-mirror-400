from abc import ABC
from gllm_multimodal.modality_converter.image_to_text.image_to_text import BaseImageToText as BaseImageToText
from gllm_multimodal.modality_converter.schema.mermaid import Mermaid as Mermaid
from gllm_multimodal.modality_converter.schema.text_result import TextResult as TextResult

class BaseImageToMermaid(BaseImageToText, ABC):
    """Abstract base class for image-to-mermaid converters.

    This class provides a standardized `_convert` implementation and defines
    the interface `_get_mermaid`, which must be implemented by subclasses.

    Subclasses should implement logic to process an image and produce a
    Mermaid syntax string that represents the structure of the diagram.
    """
