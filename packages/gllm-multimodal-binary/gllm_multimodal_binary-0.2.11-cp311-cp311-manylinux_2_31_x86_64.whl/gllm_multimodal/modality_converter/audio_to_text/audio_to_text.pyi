from abc import ABC, abstractmethod
from gllm_core.schema import Component
from gllm_multimodal.modality_converter.schema.audio_transcript import AudioTranscript as AudioTranscript

class BaseAudioToText(Component, ABC):
    """An abstract base class for audio to text used in Gen AI applications.

    This class provides a foundation for building audio to text converter components in Gen AI applications.
    """
    @abstractmethod
    async def convert(self, audio_source: str) -> list[AudioTranscript]:
        """Converts audio to text from a given source.

        This abstract method must be implemented by subclasses to define how the audio is converted to text.
        It is expected to return a list of audio transcripts.

        Args:
            audio_source (str): The source of the audio to be transcribed.

        Returns:
            list[AudioTranscript]: A list of audio transcripts.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
