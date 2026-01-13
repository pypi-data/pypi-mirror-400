from _typeshed import Incomplete
from gllm_multimodal.modality_converter.audio_to_text.audio_to_text import BaseAudioToText as BaseAudioToText
from gllm_multimodal.modality_converter.schema.audio_transcript import AudioTranscript as AudioTranscript
from gllm_multimodal.utils.audio_to_text_utils import is_youtube_url as is_youtube_url
from pydantic import BaseModel

DEFAULT_SYSTEM_PROMPT: str
DEFAULT_USER_PROMPT: str

class AudioTranscripts(BaseModel):
    """Schema for audio transcripts response from Gemini API."""
    audio_transcripts: list[AudioTranscript]

class GeminiAudioToText(BaseAudioToText):
    """A audio to text converter using Gemini."""
    model: Incomplete
    system_prompt: Incomplete
    user_prompt: Incomplete
    client: Incomplete
    logger: Incomplete
    def __init__(self, api_key: str, model: str = 'gemini-2.5-flash', system_prompt: str = ..., user_prompt: str = ..., max_retries: int = 0, timeout: float = 0) -> None:
        '''Initializes the GeminiAudioToText.

        Args:
            api_key (str): The API key for the Gemini API.
            model (str, optional): The model to use for the audio to text conversion. Defaults to "gemini-2.5-flash".
            system_prompt (str, optional): Custom system prompt for audio processing. Defaults to DEFAULT_SYSTEM_PROMPT.
            user_prompt (str, optional): Custom user prompt for audio processing. Defaults to DEFAULT_USER_PROMPT.
            max_retries (int, optional): The maximum number of retry attempts for failed requests. Defaults to 0.
            timeout (float, optional): The timeout duration for requests in seconds. Defaults to 0 (no timeout).
        '''
    async def convert(self, audio_source: str) -> list[AudioTranscript]:
        """Converts an audio source to text.

        Args:
            audio_source (str): The path to the audio file. Can be:
                - file path to a local audio file
                - a YouTube URL

        Returns:
            list[AudioTranscript]: A list of AudioTranscript.

        Raises:
            ValueError: If the provided audio source is not supported or cannot be processed.
        """
