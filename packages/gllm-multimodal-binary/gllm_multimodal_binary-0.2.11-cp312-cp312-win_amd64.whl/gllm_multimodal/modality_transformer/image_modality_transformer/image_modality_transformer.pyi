from abc import ABC
from gllm_multimodal.modality_transformer.modality_transformer import BaseModalityTransformer as BaseModalityTransformer
from typing import Any

class ImageModalityTransformer(BaseModalityTransformer, ABC):
    """Abstract base class for transforming image modality inputs into a textual representation.

    This class is designed to process image data (either as file paths or raw bytes)
    and convert it into text using one or more `BaseImageToText` converters. It serves
    a similar role to a query transformer but is specialized for handling image inputs.
    """
    async def transform(self, source: bytes | str, query: str | None = None, **kwargs: Any) -> str | bytes:
        """Transforms the given image modality source into a string or bytes.

        This abstract method must be implemented by subclasses to define how the input source is transformed. It is
        expected to return a list of transformed query strings.

        Args:
            source (bytes | str): Any single modality source to be transformed.
            query (str | None): Input query that will be used as additional information for modality transformation.
            kwargs (Any): additional arguments for converter.

        Returns:
            str | bytes: A string or bytes of transformed str or bytes source(s).

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
