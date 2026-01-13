from gllm_multimodal.modality_converter.image_to_text.image_to_caption import LMBasedImageToCaption as LMBasedImageToCaption
from gllm_multimodal.modality_converter.image_to_text.image_to_mermaid import LMBasedImageToMermaid as LMBasedImageToMermaid
from gllm_multimodal.modality_converter.modality_converter import BaseModalityConverter as BaseModalityConverter
from gllm_pipeline.router.router import BaseRouter as BaseRouter

def get_preset(preset_name: str = 'domain_specific') -> dict[str, BaseRouter | dict[str, BaseModalityConverter]]:
    """Get the preset configuration for standard transformer.

    Args:
        preset_name (str): The name of the preset to get.

    Returns:
        dict[str, BaseRouter | dict[str, BaseModalityConverter]]: A tuple containing router and route mapping.
    """
