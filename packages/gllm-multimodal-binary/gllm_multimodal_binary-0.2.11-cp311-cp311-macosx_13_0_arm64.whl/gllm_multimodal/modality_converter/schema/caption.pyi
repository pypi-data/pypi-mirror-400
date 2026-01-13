from gllm_inference.schema import Attachment
from gllm_multimodal.constants import CaptionConstants as CaptionConstants, ImageToTextConstants as ImageToTextConstants
from gllm_multimodal.utils.image_utils import get_image_binary as get_image_binary
from pydantic import BaseModel
from typing import Any

class Caption(BaseModel):
    '''Result class for image captioning operations.

    This class extends ImageToTextResult to provide a structured format
    for image captioning results, supporting:
    - Multiple caption types (one-liner, detailed, domain-specific)
    - Caption count tracking
    - Metadata storage for processing details

    Attributes:
        image_one_liner (str): Brief, single-sentence summary of the image.
            Defaults to empty string if not provided.
        image_description (str): Detailed, multi-sentence description of the image.
            Defaults to empty string if not provided.
        domain_knowledge (str): Domain-specific interpretation or context.
            Defaults to empty string if not provided.
        number_of_captions (int): Total number of distinct captions generated.
            Defaults to 0 if no captions are generated.
        image_metadata (dict[str, Any]): Additional information about the image such as image location.
        attachments_context (list[Attachment]): Optional list of external context
            objects (files, bytes, or pre-processed inputs) that can enrich
            captioning results. Bytes are automatically converted into Attachment
            objects via `Attachment.from_bytes`.

    Example:
        >>> Caption(
        ...     image_one_liner="A cat sitting on a couch",
        ...     image_description="A fluffy orange cat resting on a blue sofa in a living room.",
        ...     attachments_context=[
        ...         b"raw image bytes here",
        ...         Attachment.from_bytes(b\'some bytes\', filename="context.png"),
        ...     ]
        ... )
    '''
    image_one_liner: str
    image_description: str
    domain_knowledge: str
    number_of_captions: int
    language: str
    image_metadata: dict[str, Any]
    attachments_context: list[Attachment]
    def handle_none_values(str_value: Any) -> Any:
        """Handle None values by converting them to default values."""
    def handle_none_number_of_captions(caption_value: Any) -> Any:
        """Handle None values for number_of_captions by using default."""
    def handle_none_metadata(metadata_value: Any) -> Any:
        """Handle None values for image_metadata by using empty dict."""
    def handle_none_attachments(cls, attachments_value: Any) -> Any:
        """Normalize and validate `attachments_context`.

        This method ensures that the `attachments_context` field is always a list of
        `Attachment` objects. It handles multiple input cases:

        - None → returns an empty list
        - list[bytes] → converts each item into an Attachment via `Attachment.from_bytes`
        - list[Attachment] → keeps as-is
        - list[mixed] → normalizes supported types, raises error on unsupported types
        - any other type → raises TypeError

        Args:
            attachments_value (Any): Input value provided to `attachments_context`.

        Returns:
            list[Attachment]: A normalized list of `Attachment` objects.

        Raises:
            TypeError: If an unsupported type is provided (e.g., str, dict).
        """
