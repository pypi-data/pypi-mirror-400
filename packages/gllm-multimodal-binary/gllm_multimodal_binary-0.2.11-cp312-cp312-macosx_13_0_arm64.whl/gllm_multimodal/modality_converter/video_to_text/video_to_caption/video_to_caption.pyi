from abc import ABC
from gllm_multimodal.modality_converter.schema.caption import Caption as Caption
from gllm_multimodal.modality_converter.schema.text_result import TextResult as TextResult
from gllm_multimodal.modality_converter.schema.video_caption_result import Segment as Segment, VideoCaptionMetadata as VideoCaptionMetadata
from gllm_multimodal.modality_converter.video_to_text.video_to_text import BaseVideoToText as BaseVideoToText
from gllm_multimodal.utils.image_utils import get_image_binary as get_image_binary

class BaseVideoToCaption(BaseVideoToText, ABC):
    """Abstract base class for video captioning operations in Gen AI applications.

    This class extends BaseVideoToText to provide specialized functionality for generating
    captions from videos. It supports video segmentation, keyframe extraction, transcript
    integration, and can incorporate additional context like video title, description,
    domain knowledge, and metadata.
    """
