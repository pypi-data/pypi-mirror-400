from gllm_multimodal.modality_converter.schema.audio_transcript import AudioTranscript as AudioTranscript
from pydantic import BaseModel

class Keyframe(BaseModel):
    """Represents a keyframe extracted from a video segment.

    Attributes:
        time_offset (float): Time within the segment where the keyframe occurs.
        media_id (str | None): media id to the raw keyframe image data.
        caption (str): Text description of this specific keyframe.
    """
    time_offset: float
    media_id: str | None
    caption: str

class Segment(BaseModel):
    """Represents a video segment with its captions, transcripts, and keyframes.

    Attributes:
        start_time (float): The segment's starting time in seconds.
        end_time (float): The segment's ending time in seconds.
        transcripts (list[AudioTranscript]): Optional list of transcripts for the segment.
        segment_caption (list[str]): The single, rich description of the segment's action/plot.
        keyframes (list[Keyframe]): Optional list of keyframes extracted from the segment.
    """
    start_time: float
    end_time: float
    transcripts: list[AudioTranscript]
    segment_caption: list[str]
    keyframes: list[Keyframe]
    def ensure_caption(self) -> Segment:
        """Ensure segment has caption, fallback to keyframes/transcripts if needed."""

class VideoCaptionMetadata(BaseModel):
    """Metadata for video captioning results.

    Attributes:
        video_summary (str): A high-level summary of the entire video's plot, topic, or main events.
        segments (list[Segment]): List of video segments with their captions and metadata.
    """
    video_summary: str
    segments: list[Segment]
