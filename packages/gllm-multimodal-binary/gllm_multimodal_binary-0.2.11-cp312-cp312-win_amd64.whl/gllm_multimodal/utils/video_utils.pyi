from _typeshed import Incomplete

logger: Incomplete

def extract_video_frame_at_timestamp(video_path: str, timestamp: float, output_format: str = 'PNG') -> bytes:
    '''Extract a single frame from a video at a specific timestamp.

    This function extracts a frame from a video file at the specified timestamp
    and returns it as raw image bytes in the specified format.

    Args:
        video_path (str): Path to the video file.
        timestamp (float): Time offset in seconds from which to extract the frame.
        output_format (str, optional): Image format for the output (PNG, JPEG, etc.).
            Defaults to "PNG".

    Returns:
        bytes: Raw image bytes in the specified format.

    Raises:
        FileNotFoundError: If the video file doesn\'t exist.
        ValueError: If timestamp is negative or frame extraction fails.
        ImportError: If required libraries (cv2/opencv-python) are not installed.

    Examples:
        >>> frame_bytes = extract_video_frame_at_timestamp("video.mp4", 5.5)
        >>> frame_bytes = extract_video_frame_at_timestamp("video.mp4", 10.0, "JPEG")
    '''
