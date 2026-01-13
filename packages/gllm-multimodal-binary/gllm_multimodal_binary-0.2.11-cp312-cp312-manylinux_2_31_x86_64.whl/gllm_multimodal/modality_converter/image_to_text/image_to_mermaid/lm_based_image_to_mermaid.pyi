from _typeshed import Incomplete
from gllm_inference.request_processor.lm_request_processor import LMRequestProcessor
from gllm_inference.request_processor.uses_lm_mixin import UsesLM
from gllm_multimodal.modality_converter.image_to_text.image_to_mermaid.image_to_mermaid import BaseImageToMermaid as BaseImageToMermaid
from gllm_multimodal.modality_converter.image_to_text.image_to_mermaid.preset_image_to_mermaid import get_preset_image_to_mermaid as get_preset_image_to_mermaid
from gllm_multimodal.modality_converter.schema.mermaid import Mermaid as Mermaid
from typing import Any

class LMBasedImageToMermaid(BaseImageToMermaid, UsesLM):
    """LM-based implementation for converting an image into Mermaid diagram syntax.

    This class leverages a language model (LM) pipeline to generate structured Mermaid syntax from
    image inputs and optional metadata. It uses prompt builders, LM invokers, and output parsers
    defined via a preset system to streamline model usage.

    Inherits:
        BaseImageToMermaid: Base class defining the image-to-mermaid interface.
        UsesLM: Mixin providing shared logic for components using language models.

    Attributes:
        lm_request_processor (LMRequestProcessor): Handles prompt creation, LM invocation,
            and output parsing. Core component that orchestrates the image-to-mermaid pipeline.
    """
    lm_request_processor: Incomplete
    def __init__(self, lm_request_processor: LMRequestProcessor) -> None:
        """Initializes the LMBasedImageToMermaid instance with a language model request processor.

        Args:
            lm_request_processor (LMRequestProcessor): The processor handling prompt creation,
                LM invocation, and output parsing.
        """
    @classmethod
    def from_preset(cls, preset_name: str | None = 'default', lm_invoker_kwargs: dict | None = None, prompt_builder_kwargs: dict | None = None, **kwargs: Any) -> LMBasedImageToMermaid:
        '''Constructs an LMBasedImageToMermaid instance using a named preset configuration.

        Args:
            preset_name (str | None): Name of the predefined preset configuration to use.
                Defaults to "default".
            lm_invoker_kwargs: dict | None: Additional arguments for lm invoker.
            prompt_builder_kwargs: dict | None: Additional arguments for prompt builder.
            **kwargs (Any): Additional keyword arguments passed to the constructor.

        Returns:
            LMBasedImageToMermaid: An instance initialized with the preset\'s components.
        '''
