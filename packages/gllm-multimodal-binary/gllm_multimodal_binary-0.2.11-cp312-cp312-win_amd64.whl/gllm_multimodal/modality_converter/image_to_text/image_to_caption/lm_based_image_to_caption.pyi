from _typeshed import Incomplete
from gllm_inference.request_processor.lm_request_processor import LMRequestProcessor
from gllm_inference.request_processor.uses_lm_mixin import UsesLM
from gllm_multimodal.constants import CaptionConstants as CaptionConstants, ImageToTextConstants as ImageToTextConstants
from gllm_multimodal.modality_converter.image_to_text.image_to_caption.image_to_caption import BaseImageToCaption as BaseImageToCaption
from gllm_multimodal.modality_converter.image_to_text.image_to_caption.preset_image_to_caption import get_preset_image_to_caption as get_preset_image_to_caption
from gllm_multimodal.modality_converter.schema.caption import Caption as Caption
from typing import Any

class LMBasedImageToCaption(BaseImageToCaption, UsesLM):
    """Image captioning implementation using Language Models.

    This class implements the ImageToCaption interface using LMs for generating
    natural language captions.
    """
    lm_request_processor: Incomplete
    def __init__(self, lm_request_processor: LMRequestProcessor) -> None:
        """Initialize the LM based image captioning component.

        Args:
            lm_request_processor: Language model request processor instance that supports multimodal inputs.
            prompt_builder: Base prompt builder for constructing model inputs. For best results,
                the prompt should include all of the following placeholders in curly braces {}:
                1. filename: Name of the image file.
                2. number_of_captions: Number of captions to generate.
                3. image_oneliner: Brief one-line summary.
                4. image_description: Detailed description.
                5. domain_knowledge: Domain-specific context.
                6. metadata: Image metadata as JSON string.
            event_emitter: Optional event emitter for streaming responses.
            caption_json_key: Key in the JSON response containing captions. Defaults to 'captions'.
        """
    @classmethod
    def from_preset(cls, preset_name: str | None = 'default', **kwargs: Any) -> LMBasedImageToCaption:
        """Initialize the LM based image captioning component using preset model configurations.

        Args:
            preset_name (str): Name of the preset to use.
            **kwargs (Any): Additional keyword arguments to pass to from_lm_components().

        Returns:
            LMBasedImageToCaption: Initialized image captioning component using preset model.
        """
