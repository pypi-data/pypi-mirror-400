from _typeshed import Incomplete
from gllm_multimodal.modality_converter.audio_to_text.audio_to_text import BaseAudioToText as BaseAudioToText
from gllm_multimodal.modality_converter.schema.audio_transcript import AudioTranscript as AudioTranscript
from gllm_multimodal.utils.audio_to_text_utils import convert_audio_to_mono_flac as convert_audio_to_mono_flac, get_audio_from_base64 as get_audio_from_base64, get_audio_from_downloadable_url as get_audio_from_downloadable_url, get_audio_from_file_path as get_audio_from_file_path, get_audio_from_youtube_url as get_audio_from_youtube_url

MAX_AUDIO_SIZE: Incomplete

class OpenAIWhisperAudioToText(BaseAudioToText):
    """An audio to text converter using OpenAI Whisper.

    The OpenAIWhisperAudioToText class is responsible for converting audio to text using OpenAI Whisper.
    It supports various audio sources such as file paths, base64 encoded strings, downloadable audio URLs,
    and YouTube URLs.

    Attributes:
        client (OpenAI): The OpenAI client instance used for API requests.
        model (str): The identifier of the OpenAI Whisper model to use for transcription.
        language (str | None): The language of the input audio content.
        prompt (str | None): The text prompt to guide the model's style or continue a previous audio segment.
        temperature (float): The sampling temperature to control output randomness.
        timestamp_granularity (str): The timestamp detail levels to include in the output.
        proxy (str | None): The proxy URL to use for the YouTube request.
    """
    client: Incomplete
    model: Incomplete
    language: Incomplete
    prompt: Incomplete
    temperature: Incomplete
    timestamp_granularity: Incomplete
    proxy: Incomplete
    logger: Incomplete
    def __init__(self, api_key: str, model: str = 'whisper-1', language: str | None = None, prompt: str | None = None, temperature: float = 0, timestamp_granularity: str = 'segment', proxy: str | None = None) -> None:
        '''Initialize the OpenAIWhisperAudioToText instance.

        Args:
            api_key (str): The API key for authentication with OpenAI.
            model (str, optional): The model identifier to use for transcription. Defaults to "whisper-1".
            language (str | None, optional): The language of the input audio content. Defaults to None.
            prompt (str | None, optional): The text prompt to guide the model\'s style or continue a previous audio
                segment. The prompt should match the audio language. Defaults to None.
            temperature (float, optional): The sampling temperature to control output randomness. Defaults to 0.
            timestamp_granularity (str, optional): The timestamp detail levels to include in the output.
                The granularity can be "segment" or "word". When set to "segment", OpenAI will return
                transcripts divided into segments of speech. When set to "word", it will include word-level
                timestamps. Defaults to "segment".
            proxy (str | None, optional): The proxy URL to use for the YouTube request. Defaults to None.
        '''
    async def convert(self, audio_source: str) -> list[AudioTranscript]:
        """Convert audio to text using OpenAI Whisper.

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
