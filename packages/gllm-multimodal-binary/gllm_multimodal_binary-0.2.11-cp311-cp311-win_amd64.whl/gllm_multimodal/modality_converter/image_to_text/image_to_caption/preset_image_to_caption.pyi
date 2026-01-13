from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from gllm_inference.prompt_builder import PromptBuilder

DEFAULT_SYSTEM_PROMPT: str
DEFAULT_USER_PROMPT: str

def create_default_prompt_builder() -> PromptBuilder:
    """Create a default prompt builder with templates for generating image captions.

    This function creates and returns an PromptBuilder instance configured with
    default templates for image captioning tasks. The templates are structured to:

    System prompt:
    1. Instructs the model to generate the specified number of captions.
    2. Specifies output format as a JSON list of captions.

    User prompt:
    1. Provides structured input format with fields for:
        1. Image one-liner
        2. Image description
        3. Domain knowledge (will be generated from the image given)
        4. Filename (will be generated from the image given)
        5. Image metadata (will be generated from the image given)

    Returns:
        PromptBuilder: A prompt builder instance configured with default
            templates for image captioning.
    """
def get_preset_image_to_caption(preset_name: str | None) -> tuple[BaseLMInvoker, PromptBuilder, BaseOutputParser]:
    """Get the preset configuration for generating image captions.

    Args:
        preset_name (str): The name of the preset to get.

    Returns:
        tuple[BaseLMInvoker, PromptBuilder, BaseOutputParser]: A tuple containing the preset
            configuration for image captioning.
    """
