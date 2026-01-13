from _typeshed import Incomplete

logger: Incomplete

def is_binary_data_audio(audio_binary_data: bytes) -> bool:
    """Check if the binary data is a valid audio file.

    Args:
        audio_binary_data (bytes): The binary data to check.

    Returns:
        bool: True if the binary data is a valid audio file, False otherwise.
    """
def get_audio_from_base64(audio_source: str) -> bytes | None:
    """Attempt to decode a base64 encoded audio string and verify if it's valid audio data.

    Args:
        audio_source (str): The potential base64 encoded audio string to decode.

    Returns:
        bytes | None: The decoded audio data if successful and valid, None otherwise.
    """
def get_audio_from_file_path(audio_source: str) -> bytes | None:
    """Read audio file and return its binary data if valid.

    Args:
        audio_source (str): Path to the audio file.

    Returns:
        bytes | None: Binary data of the audio file if valid, None otherwise.
    """
def get_audio_from_downloadable_url(audio_source: str, timeout: int = ...) -> bytes | None:
    """Get the audio from a downloadable URL and return its binary data if valid.

    This function attempts to download audio content from a downloadable URL (e.g. Google Drive, OneDrive)
    and validates that the downloaded content is audio data.

    Args:
        audio_source (str): The downloadable URL of the audio file.
        timeout (int): The timeout for the HTTP request in seconds. Defaults to 1 minute.

    Returns:
        bytes | None: Binary data of the audio file if valid audio content is downloaded,
            None if the request fails or content is not valid audio.
    """
def get_audio_from_youtube_url(audio_source: str, proxy: str | None = None) -> bytes | None:
    """Extract audio from a YouTube video URL and return it as binary data.

    This function downloads a YouTube video and extracts its audio track in M4A format.
    The audio is stored in memory and validated before being returned.

    Args:
        audio_source (str): The YouTube video URL to extract audio from.
        proxy (str | None, optional): The proxy URL to use for the YouTube request. Defaults to None.

    Returns:
        bytes | None: Binary audio data if successfully downloaded and valid,
            None if download fails or audio is invalid.
    """
def get_audio_duration(audio_binary_data: bytes) -> float:
    """Get the duration of the audio in seconds.

    Args:
        audio_binary_data (bytes): The binary data of the audio.

    Returns:
        float: The duration of the audio in seconds.
    """
def convert_audio_to_mono_flac(input_audio_bytes: bytes) -> bytes:
    """Convert audio binary data to mono FLAC format.

    This method standardizes the audio format to mono FLAC to simplify processing by having a consistent
    file extension and single audio channel, while preserving the audio information.

    This method performs two operations:
    1. Converts the input audio to mono (single channel)
    2. Encodes the audio in FLAC format for optimal speech recognition

    FLAC (Free Lossless Audio Codec) is chosen because:
    1. Lossless compression preserves audio quality for accurate transcription
    2. More bandwidth efficient compared to uncompressed formats like LINEAR16
    3. supports variable bit depths (16/24-bit) automatically -> no need to specify sample rate

    Mono channel is chosen because:
    1. Speech recognition models are optimized for single-channel audio
    2. Reduces bandwidth and processing overhead
    3. Simplifies processing by avoiding multi-channel complexity
    4. Ensures consistent results across different input formats

    Args:
        input_audio_bytes (bytes): Input audio data in binary format.

    Returns:
        bytes: Audio data converted to mono FLAC format.
    """
def is_youtube_url(source: str) -> bool:
    """Check if the audio source is a YouTube URL.

    Args:
        source (str): The audio source to check.

    Returns:
        bool: True if the audio source is a YouTube URL, False otherwise.
    """
