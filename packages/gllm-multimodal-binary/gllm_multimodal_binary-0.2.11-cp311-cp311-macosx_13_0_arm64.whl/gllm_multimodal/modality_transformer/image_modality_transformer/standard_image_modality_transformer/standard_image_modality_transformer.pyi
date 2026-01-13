from _typeshed import Incomplete
from gllm_multimodal.modality_converter.modality_converter import BaseModalityConverter as BaseModalityConverter
from gllm_multimodal.modality_converter.schema import TextResult as TextResult
from gllm_multimodal.modality_transformer.image_modality_transformer.image_modality_transformer import ImageModalityTransformer as ImageModalityTransformer
from gllm_multimodal.modality_transformer.image_modality_transformer.standard_image_modality_transformer.preset import get_preset as get_preset
from gllm_pipeline.router.router import BaseRouter

class StandardImageModalityTransformer(ImageModalityTransformer):
    """A standardized image modality transformer that routes and applies converter.

    This class integrates a routing mechanism to dynamically select a converter
    according to the characteristics of the image input (e.g., format, content, etc.).

    Attributes:
        router (BaseRouter): A routing component that determines the route based on the input image.
        route_mapping (dict[str, BaseModalityConverter]): A mapping of route names to their corresponding
            modality converters.
    """
    router: Incomplete
    route_mapping: Incomplete
    def __init__(self, router: BaseRouter, route_mapping: dict[str, BaseModalityConverter]) -> None:
        """Initialize the StandardImageModalityTransformer.

        Args:
            router (BaseRouter): The router responsible for selecting the route.
            route_mapping (dict[str, BaseModalityConverter]): Mapping from route names to modality converters.

        Raises:
            ValueError: If any expected route from the router is missing in the route_mapping.
        """
    @classmethod
    def from_preset(cls, preset_name: str) -> StandardImageModalityTransformer:
        """Create an instance using a predefined preset configuration.

        Args:
            preset_name (str): Name of the preset to use.

        Returns:
            StandardImageModalityTransformer: An instance configured with the preset.
        """
