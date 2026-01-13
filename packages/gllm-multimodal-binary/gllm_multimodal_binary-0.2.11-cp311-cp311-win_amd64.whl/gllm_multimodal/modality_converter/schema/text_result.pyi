from pydantic import BaseModel
from typing import Any

class TextResult(BaseModel):
    """Base class for all image-to-text operation results.

    This class provides the foundation for structured results from any
    image-to-text operation, including:
        - Image Captioning
        - Scene Text Detection

    Attributes:
        text (str): The extracted or generated text from the image.
            This is the primary output of any image-to-text operation.
            May be empty if the operation fails or no text is found.
        metadata (dict[str, Any] | BaseModel): Additional metadata from the conversion process.
    """
    result: str
    tag: str
    metadata: dict[str, Any] | BaseModel | None
