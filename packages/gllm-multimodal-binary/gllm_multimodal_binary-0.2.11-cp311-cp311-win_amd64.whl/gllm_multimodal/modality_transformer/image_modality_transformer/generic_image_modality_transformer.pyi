from _typeshed import Incomplete
from gllm_multimodal.modality_converter.modality_converter import BaseModalityConverter as BaseModalityConverter
from gllm_multimodal.modality_transformer.image_modality_transformer.image_modality_transformer import ImageModalityTransformer as ImageModalityTransformer

class GenericImageModalityTransformer(ImageModalityTransformer):
    """A generic transformer which uses a single converter to convert images to string/bytes.

    Attributes:
        converter (BaseModalityConverter): The converter used to transform images into text or bytes.
    """
    converter: Incomplete
    def __init__(self, converter: BaseModalityConverter) -> None:
        """Initializes the transformer with a modality converter.

        Args:
            converter (BaseModalityConverter): An instance of a modality converter responsible
                for performing the image-to-text or image-to-bytes transformation.
        """
