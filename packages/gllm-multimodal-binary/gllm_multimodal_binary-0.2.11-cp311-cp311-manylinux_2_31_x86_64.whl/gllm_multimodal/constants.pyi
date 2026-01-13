from enum import StrEnum

class ImageToTextConstants:
    """Constants for image-to-text operations in Gen AI applications."""
    NOT_GIVEN: str
    FILENAME: str
    NO_IMAGE_FILENAME: str

class CaptionConstants:
    """Constants for caption operations in Gen AI applications."""
    CAPTION_DEFAULT_JSON_KEY: str
    DOMAIN_KNOWLEDGE: str
    IMAGE_DESCRIPTION: str
    IMAGE_METADATA: str
    IMAGE_ONE_LINER: str
    NUMBER_OF_CAPTIONS: str
    ATTACHMENTS_CONTEXT: str
    DEFAULT_NUMBER_OF_CAPTIONS: int

class ExifConstants:
    """Constants for EXIF tag operations in image metadata extraction."""
    GPS_LATITUDE: str
    GPS_LATITUDE_REF: str
    GPS_LONGITUDE: str
    GPS_LONGITUDE_REF: str
    GPS_SOUTH: str
    GPS_WEST: str
    LATITUDE: str
    LONGITUDE: str

class Modality(StrEnum):
    """Defines supported modalities."""
    IMAGE: str
    TEXT: str
    AUDIO: str
    VIDEO: str

class ModalityConverterApproach(StrEnum):
    """Defines supported modality converter approach types."""
    LM_BASED: str
    WHISPER: str
    GEMINI: str
    GOOGLE_CLOUD: str
    PROSA: str
    YOUTUBE: str

class ModalityConverterTask(StrEnum):
    """Defines supported modality converter tasks."""
    CAPTIONING: str
    MERMAID: str
    TRANSCRIPT: str
    AUTO: str
