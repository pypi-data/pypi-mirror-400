from gllm_multimodal.constants import Modality as Modality, ModalityConverterApproach as ModalityConverterApproach, ModalityConverterTask as ModalityConverterTask
from gllm_multimodal.modality_converter.image_to_text.image_to_caption import LMBasedImageToCaption as LMBasedImageToCaption
from gllm_multimodal.modality_converter.image_to_text.image_to_mermaid import LMBasedImageToMermaid as LMBasedImageToMermaid
from gllm_multimodal.modality_converter.modality_converter import BaseModalityConverter as BaseModalityConverter

ConverterKey = tuple[Modality, Modality, ModalityConverterTask, ModalityConverterApproach | None]
ConverterClass = type[BaseModalityConverter]
MODALITY_CONVERTER_REGISTRY: dict

def build_modality_converter(source_modality: Modality, target_modality: Modality, task_type: ModalityConverterTask = ..., approach_type: ModalityConverterApproach | None = None, preset: str | None = None, **kwargs) -> BaseModalityConverter:
    """Build and initialize a modality converter instance for a given configuration.

    The factory looks up the converter class based on the combination of:
        - source_modality: input modality (e.g., Modality.IMAGE, Modality.AUDIO)
        - target_modality: output modality (e.g., Modality.TEXT)
        - task_type: conversion task (e.g., CAPTIONING, TRANSCRIPT, MERMAID, or AUTO)
        - approach_type: the converter's algorithmic approach; required for non-AUTO tasks, must be None for AUTO

    All supported combinations must be registered in MODALITY_CONVERTER_REGISTRY.

    Args:
        source_modality (Modality): The source modality.
        target_modality (Modality): The output modality.
        task_type (ModalityConverterTask, optional): The conversion task. Defaults to ModalityConverterTask.AUTO.
        approach_type (ModalityConverterApproach | None, optional): The approach for the conversion.
            Required for non-AUTO tasks; must be None for task_type=AUTO.
        preset (str | None, optional): Preset identifier for the converter's .from_preset() method.
            If None, uses the default preset for the class.
        **kwargs: Additional keyword arguments passed to .from_preset().

    Returns:
        BaseModalityConverter: An instance of the matching converter class.

    Raises:
        ValueError: If the configuration is invalid or not registered, including:
            - (source_modality, target_modality, task_type, approach) not registered
            - approach_type missing for non-AUTO task_type
            - approach_type provided when task_type is AUTO
            - Any dimension unsupported for the given combination
    """
