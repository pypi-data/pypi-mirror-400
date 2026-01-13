from _typeshed import Incomplete
from gllm_multimodal.modality_converter.audio_to_text.audio_to_text import BaseAudioToText as BaseAudioToText
from gllm_multimodal.modality_converter.schema.audio_transcript import AudioTranscript as AudioTranscript
from gllm_multimodal.utils.audio_to_text_utils import get_audio_duration as get_audio_duration, get_audio_from_base64 as get_audio_from_base64, get_audio_from_file_path as get_audio_from_file_path

MAX_BASE64_AUDIO_DURATION: int
MIN_POLLING_INTERVAL: int

class ProsaAudioToText(BaseAudioToText):
    """An audio to text converter using Prosa STT.

    The ProsaAudioToText class is responsible for converting audio to text using the Prosa STT API.
    It supports various audio input formats and can handle audio from local files, base64 encoded strings,
    or URLs pointing to audio files.

    Attributes:
        url (str): The URL of the Prosa STT API.
        api_key (str): The API key for authenticating with the Prosa STT API.
        model (str): The model to use for the transcription.
        polling_interval (int): The interval between polling requests to the Prosa STT API.
    """
    api_key: Incomplete
    url: Incomplete
    model: Incomplete
    logger: Incomplete
    def __init__(self, api_key: str, url: str = 'https://api.prosa.ai/v2/speech/stt', model: str = 'stt-general', polling_interval: int = ...) -> None:
        '''Initializes a new instance of the ProsaAudioToText class.

        Args:
            api_key (str): The API key for the Prosa STT API.
            url (str, optional): The URL of the Prosa STT API. Defaults to "https://api.prosa.ai/v2/speech/stt".
            model (str, optional): The model to use for the transcription. Defaults to "stt-general".
            polling_interval (int, optional): The interval between polling requests to the Prosa STT API.
                Defaults to MIN_POLLING_INTERVAL, which is set to 5 seconds.
        '''
    @property
    def polling_interval(self) -> int:
        """Get the polling interval in seconds.

        Returns:
            int: The current polling interval.
        """
    @polling_interval.setter
    def polling_interval(self, polling_interval: int):
        """Set the polling interval in seconds.

        Args:
            polling_interval (int): The new polling interval.

        Raises:
            ValueError: If the polling interval is not an int or is less than 5.
        """
    async def convert(self, audio_source: str) -> list[AudioTranscript]:
        """Convert audio to text using the Prosa STT API.

        This method processes the given audio source and returns the transcribed text.
        The audio source can be a local file path, a base64 encoded string, or a URL.

        Args:
            audio_source (str): The source of the audio to be transcribed. Can be:
                - A path to a local audio file with maximum duration of 55 seconds.
                - A base64 encoded string of audio data with maximum duration of 55 seconds.
                - A direct HTTP/HTTPS URL that returns an audio file:
                    * Google Drive shared file URLs (e.g. https://drive.google.com/file/d/...)
                    * OneDrive shared file URLs (e.g. https://onedrive.live.com/...)
                    * S3 URLs (e.g. https://s3.amazonaws.com/...)
                    * Other HTTP URLs that directly serve audio files

        Returns:
            list[AudioTranscript]: A list of AudioTranscript objects containing the transcribed text.

        Raises:
            ValueError:
                - If the audio source is file path but the audio duration exceeds 55 seconds.
                - If the audio source is base64 encoded string but the audio duration exceeds 55 seconds.
                - If the audio source is not supported.
        """
