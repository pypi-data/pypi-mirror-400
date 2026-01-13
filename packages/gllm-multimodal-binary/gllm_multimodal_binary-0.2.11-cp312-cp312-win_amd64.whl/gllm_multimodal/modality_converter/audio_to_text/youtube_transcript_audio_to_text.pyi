from _typeshed import Incomplete
from gllm_multimodal.modality_converter.audio_to_text.audio_to_text import BaseAudioToText as BaseAudioToText
from gllm_multimodal.modality_converter.schema.audio_transcript import AudioTranscript as AudioTranscript

class YouTubeTranscriptAudioToText(BaseAudioToText):
    """An audio to text converter using YouTube Transcript API.

    The YoutubeTranscriptAudioToText class is responsible for converting audio from YouTube to text using
    YouTube Transcript API.

    Attributes:
        preferred_lang_ids (list[str]): The preferred language IDs for the transcript.
        allow_non_preferred_lang_ids (bool): Whether to allow non-preferred language IDs.
        allow_auto_generated_transcripts (bool): Whether to allow auto-generated transcripts.
        proxy (str | None): The proxy URL to use for the YouTube request.
    """
    preferred_lang_ids: Incomplete
    allow_non_preferred_lang_ids: Incomplete
    allow_auto_generated_transcripts: Incomplete
    proxy: Incomplete
    youtube_transcript_api: Incomplete
    logger: Incomplete
    def __init__(self, preferred_lang_ids: list[str] | None = None, allow_non_preferred_lang_ids: bool = False, allow_auto_generated_transcripts: bool = False, proxy: str | None = None) -> None:
        '''Initialize the YouTubeTranscriptAudioToText instance.

        Args:
            preferred_lang_ids (list[str] | None, optional): The preferred language IDs for the transcript.
                Defaults to None, in which case ["id", "en"] will be used.
            allow_non_preferred_lang_ids (bool, optional): Whether to allow non-preferred language IDs.
                Defaults to False.
            allow_auto_generated_transcripts (bool, optional): Whether to allow auto-generated transcripts.
                Defaults to False.
            proxy (str | None, optional): The proxy URL to use for the YouTube request. Defaults to None.
        '''
    async def convert(self, audio_source: str) -> list[AudioTranscript]:
        """Convert YouTube audio to text using the YouTube Transcript API.

        This method takes a YouTube URL as the audio source and retrieves the transcript
        using the YouTube Transcript API. It returns the transcript as a list of AudioTranscript.

        Args:
            audio_source (str): The YouTube URL of the audio source.

        Returns:
            list[AudioTranscript]: A list of AudioTranscript.
        """
