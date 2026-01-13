from abc import ABC
from gllm_multimodal.modality_converter.image_to_text.image_to_text import BaseImageToText as BaseImageToText
from gllm_multimodal.modality_converter.schema.caption import Caption as Caption
from gllm_multimodal.modality_converter.schema.text_result import TextResult as TextResult
from gllm_multimodal.utils.image_metadata_utils import get_image_metadata as get_image_metadata
from gllm_multimodal.utils.image_utils import combine_strings as combine_strings, get_unique_non_empty_strings as get_unique_non_empty_strings

class BaseImageToCaption(BaseImageToText, ABC):
    """Abstract base class for image captioning operations in Gen AI applications.

    This class extends ImageToText to provide specialized functionality for generating
    captions from images. It supports multiple captioning styles and can incorporate additional context
    like oneliner of image, description of image, domain knowledge and metadata.
    """
