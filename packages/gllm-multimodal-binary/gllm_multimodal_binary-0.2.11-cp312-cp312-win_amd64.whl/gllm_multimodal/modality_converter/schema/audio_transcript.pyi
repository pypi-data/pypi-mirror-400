from pydantic import BaseModel

class AudioTranscript(BaseModel):
    """A class representing an audio transcript.

    An audio transcript is a textual record of spoken content from audio or video sources,
    including timing information and optional language identification. It provides a
    structured way to store and manage transcribed audio data.

    Attributes:
        text (str): The text of the transcript.
        start_time (float): The start time of the transcript in seconds.
        end_time (float): The end time of the transcript in seconds.
        lang_id (str | None): The language ID of the transcript.
    """
    text: str
    start_time: float
    end_time: float
    lang_id: str | None
