from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from gllm_inference.prompt_builder import PromptBuilder
from typing import Any

DEFAULT_SYSTEM_PROMPT: str
DEFAULT_USER_PROMPT: str

def create_default_prompt_builder(**kwargs: Any) -> PromptBuilder:
    """Create a default prompt builder with templates for generating video captions.

    This function creates and returns a PromptBuilder instance configured with
    default templates for video captioning tasks. The templates are structured to:

    System prompt:
    1. Instructs the model to generate the specified number of captions.
    2. Specifies output format as a JSON list of captions.

    User prompt:
    1. Provides structured input format with fields for:
        1. Video one-liner
        2. Video description
        3. Domain knowledge (will be generated from the video given)
        4. Filename (will be generated from the video given)
        5. Video metadata (will be generated from the video given)

    Returns:
        PromptBuilder: A prompt builder instance configured with default
            templates for video captioning.
    """
def get_preset_video_to_caption(preset_name: str, lm_invoker_kwargs: dict | None = None, prompt_builder_kwargs: dict | None = None) -> tuple[BaseLMInvoker, PromptBuilder, BaseOutputParser]:
    """Get the preset configuration for generating video captions.

    Args:
        preset_name (str): The name of the preset to get.
        lm_invoker_kwargs: dict | None: Additional arguments for lm invoker.
        prompt_builder_kwargs: dict | None: Additional arguments for prompt builder.

    Returns:
        tuple[BaseLMInvoker, PromptBuilder, BaseOutputParser]: A tuple containing the preset
            configuration for video captioning.
    """
