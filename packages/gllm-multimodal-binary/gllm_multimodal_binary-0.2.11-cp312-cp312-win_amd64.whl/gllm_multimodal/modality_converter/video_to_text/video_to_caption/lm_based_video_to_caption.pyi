from _typeshed import Incomplete
from gllm_inference.lm_invoker import GoogleLMInvoker as GoogleLMInvoker
from gllm_inference.request_processor.lm_request_processor import LMRequestProcessor
from gllm_inference.request_processor.uses_lm_mixin import UsesLM
from gllm_multimodal.constants import ImageToTextConstants as ImageToTextConstants
from gllm_multimodal.modality_converter.schema.caption import Caption as Caption
from gllm_multimodal.modality_converter.video_to_text.video_to_caption.preset_video_to_caption import get_preset_video_to_caption as get_preset_video_to_caption
from gllm_multimodal.modality_converter.video_to_text.video_to_caption.video_to_caption import BaseVideoToCaption as BaseVideoToCaption
from typing import Any

DEFAULT_FILENAME: str

class LMBasedVideoToCaption(BaseVideoToCaption, UsesLM):
    """Video captioning implementation using Language Models.

    This class implements the VideoToCaption interface using LMs for generating
    natural language captions.
    """
    lm_request_processor: Incomplete
    def __init__(self, lm_request_processor: LMRequestProcessor) -> None:
        """Initialize the LM based video captioning component.

        Args:
            lm_request_processor: Language model request processor instance that supports multimodal inputs.
        """
    @classmethod
    def from_preset(cls, preset_name: str | None = 'default', **kwargs: Any) -> LMBasedVideoToCaption:
        """Initialize the LM based video captioning component using preset model configurations.

        Args:
            preset_name (str): Name of the preset to use.
            **kwargs (Any): Additional keyword arguments to pass to from_lm_components().

        Returns:
            LMBasedVideoToCaption: Initialized video captioning component using preset model.
        """
