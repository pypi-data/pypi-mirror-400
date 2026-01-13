from _typeshed import Incomplete
from gllm_multimodal.modality_converter.audio_to_text.audio_to_text import BaseAudioToText as BaseAudioToText
from gllm_multimodal.modality_converter.schema.audio_transcript import AudioTranscript as AudioTranscript
from gllm_multimodal.utils.audio_to_text_utils import convert_audio_to_mono_flac as convert_audio_to_mono_flac, get_audio_duration as get_audio_duration, get_audio_from_base64 as get_audio_from_base64, get_audio_from_downloadable_url as get_audio_from_downloadable_url, get_audio_from_file_path as get_audio_from_file_path, get_audio_from_youtube_url as get_audio_from_youtube_url

MAX_AUDIO_DURATION: int

class GoogleCloudAudioToText(BaseAudioToText):
    """An audio to text converter using Google Cloud Speech-to-Text.

    The GoogleCloudAudioToText class is responsible for converting audio to text using the Google Cloud Speech-to-Text.
    It supports various audio input formats and can handle audio from local files, base64 encoded strings,
    or URLs pointing to audio files.

    Attributes:
        speech_client (SpeechClient): Google Cloud Speech-to-Text client.
        storage_client (storage.Client): Google Cloud Storage client.
        bucket_name (str): Google Cloud Storage bucket name.
        language_code (str): Language code for transcription.
        alternative_language_codes (list[str] | None): Alternative language codes for transcription.
            Up to 3 alternatives.
        model (str): Transcription model name.
        timeout (int): Timeout for the transcription request.
        proxy (str | None): The proxy URL to use for the YouTube request.
    """
    speech_client: Incomplete
    storage_client: Incomplete
    bucket_name: Incomplete
    language_code: Incomplete
    alternative_language_codes: Incomplete
    model: Incomplete
    timeout: Incomplete
    proxy: Incomplete
    logger: Incomplete
    def __init__(self, credentials_json: str | dict, bucket_name: str, language_code: str = 'id-ID', alternative_language_codes: list[str] | None = None, model: str = 'latest_long', timeout: int = ..., proxy: str | None = None) -> None:
        '''Initialize the GoogleCloudAudioToText instance.

        Args:
            credentials_json (str | dict): Google Cloud API credentials can either be a file path or a dictionary.
            bucket_name (str): Google Cloud Storage bucket name.
            language_code (str, optional): Language code for transcription. Defaults to "id-ID".
            alternative_language_codes (list[str] | None, optional): Alternative language codes for transcription.
                Up to 3 alternatives. If the list has more than 3 elements, the first 3 will be used.
                Defaults to None, in which ["id-ID", "en-US", "en-GB"] is used.
            model (str, optional): Transcription model name. Defaults to "latest_long".
            timeout (int, optional): Timeout for the transcription request. Defaults to 5 minutes.
            proxy (str | None, optional): The proxy URL to use for the YouTube request. Defaults to None.
        '''
    async def convert(self, audio_source: str) -> list[AudioTranscript]:
        """Convert audio to text using Google Cloud Speech-to-Text.

        This method process the given audio source and return a list of AudioTranscript.
        The audio source can be a file path, a base64 encoded string, or a URL.

        Args:
            audio_source (str): The source of the audio to convert. Can be:
                - A file path to an audio file.
                - A base64 encoded string of the audio.
                - A downloadable audio URL (e.g. Google Drive, OneDrive).
                - A YouTube URL.

        Returns:
            list[AudioTranscript]: A list of AudioTranscript.

        Raises:
            ValueError: If the provided audio source is not supported or cannot be processed.
        """
