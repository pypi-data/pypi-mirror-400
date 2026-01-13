from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from gllm_inference.prompt_builder import PromptBuilder
from typing import Any

DEFAULT_SYSTEM_PROMPT: str
DEFAULT_USER_PROMPT: str

def create_default_prompt_builder(**kwargs: Any) -> PromptBuilder:
    """Create a default prompt builder with templates for generating mermaid syntax.

    This function creates and returns an PromptBuilder instance configured with
    default templates for image to mermaid tasks. The templates are structured to:

    System prompt:
    - Specifies output format
    - Specifies rule of Mermaid syntax

    User prompt:
    - Provides structured input format with fields for:
        - diagram_type

    Args:
        **kwargs (Any): additional args for prompt builder.

    Returns:
        PromptBuilder: A prompt builder instance configured with default
            templates for image to mermaid.
    """
def get_preset_image_to_mermaid(preset_name: str | None, lm_invoker_kwargs: dict | None = None, prompt_builder_kwargs: dict | None = None) -> tuple[BaseLMInvoker, PromptBuilder, BaseOutputParser | None]:
    """Get the preset configuration for generating image to mermaid.

    Args:
        preset_name (str): The name of the preset to get.
        lm_invoker_kwargs: dict | None: Additional arguments for lm invoker.
        prompt_builder_kwargs: dict | None: Additional arguments for prompt builder.

    Returns:
        tuple[BaseLMInvoker, PromptBuilder, BaseOutputParser | None]: A tuple containing the preset
            configuration for image to mermaid.
    """
