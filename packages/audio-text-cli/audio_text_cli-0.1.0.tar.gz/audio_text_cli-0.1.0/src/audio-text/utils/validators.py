"""Input validation utilities."""

import re
from urllib.parse import parse_qs, urlparse


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_youtube_url(url: str) -> str:
    """Validate and normalize YouTube URL.

    Args:
        url: URL to validate.

    Returns:
        Normalized YouTube URL.

    Raises:
        ValidationError: If URL is not a valid YouTube URL.
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    url = url.strip()

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}") from e

    # Check for valid YouTube domains
    valid_domains = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    ]

    domain = parsed.netloc.lower()
    if domain not in valid_domains:
        raise ValidationError(
            f"Not a YouTube URL. Supported domains: {', '.join(valid_domains)}"
        )

    # Extract video ID
    video_id = None

    if "youtu.be" in domain:
        # Short URL format: https://youtu.be/VIDEO_ID
        video_id = parsed.path.strip("/")
    elif "youtube.com" in domain:
        if parsed.path == "/watch":
            # Standard format: https://www.youtube.com/watch?v=VIDEO_ID
            query_params = parse_qs(parsed.query)
            video_id = query_params.get("v", [None])[0]
        elif parsed.path.startswith("/embed/"):
            # Embed format: https://www.youtube.com/embed/VIDEO_ID
            video_id = parsed.path.replace("/embed/", "").split("/")[0]
        elif parsed.path.startswith("/v/"):
            # Old format: https://www.youtube.com/v/VIDEO_ID
            video_id = parsed.path.replace("/v/", "").split("/")[0]
        elif parsed.path.startswith("/shorts/"):
            # Shorts format: https://www.youtube.com/shorts/VIDEO_ID
            video_id = parsed.path.replace("/shorts/", "").split("/")[0]

    if not video_id:
        raise ValidationError("Could not extract video ID from URL")

    # Validate video ID format (typically 11 characters, alphanumeric + _ and -)
    if not re.match(r"^[a-zA-Z0-9_-]{10,12}$", video_id):
        raise ValidationError(f"Invalid video ID format: {video_id}")

    # Return normalized URL
    return f"https://www.youtube.com/watch?v={video_id}"


def validate_output_path(path: str) -> str:
    """Validate output directory path.

    Args:
        path: Directory path to validate.

    Returns:
        Validated path string.

    Raises:
        ValidationError: If path is invalid.
    """
    if not path:
        raise ValidationError("Output path cannot be empty")

    # Basic validation - actual directory creation handled elsewhere
    path = path.strip()

    # Check for invalid characters (basic check)
    invalid_chars = '<>"|?*'
    for char in invalid_chars:
        if char in path:
            raise ValidationError(f"Invalid character in path: {char}")

    return path
