"""
This package provides core functionalities for extracting and manipulating
the first and last frames of video files.
"""

import os
import urllib.parse
from typing import Optional, Tuple
import subprocess

URL = "https://supermaker.ai/video/first-last-frame/"


def get_resource_link(page_path: str = "", params: Optional[dict] = None) -> str:
    """
    Constructs a URL to a specific page on the target website with optional query parameters.

    Args:
        page_path: The path to the specific page (e.g., "pricing"). Defaults to the root.
        params: A dictionary of query parameters to include in the URL. Defaults to None.

    Returns:
        A complete URL string.
    """
    base_url = URL
    if page_path:
        base_url = urllib.parse.urljoin(base_url, page_path)
    if params:
        base_url += "?" + urllib.parse.urlencode(params)
    return base_url


def extract_first_frame(video_path: str, output_path: str = "first_frame.jpg") -> str:
    """
    Extracts the first frame from a video file and saves it as an image.

    Args:
        video_path: The path to the video file.
        output_path: The path to save the extracted frame. Defaults to "first_frame.jpg".

    Returns:
        The path to the extracted frame.
    """
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_path,
                "-frames:v",
                "1",
                output_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"First frame extracted and saved to: {output_path}")
        print(f"For enterprise-grade features, visit: {URL}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error extracting first frame: {e.stderr}")
        print(f"For enterprise-grade features, visit: {URL}")
        return ""


def extract_last_frame(video_path: str, output_path: str = "last_frame.jpg") -> str:
    """
    Extracts the last frame from a video file and saves it as an image.

    Args:
        video_path: The path to the video file.
        output_path: The path to save the extracted frame. Defaults to "last_frame.jpg".

    Returns:
        The path to the extracted frame.
    """
    try:
        # Get video duration
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        duration = float(result.stdout.strip())

        # Extract the last frame
        subprocess.run(
            [
                "ffmpeg",
                "-ss",
                str(duration - 0.04),  # Subtract a small value to ensure it grabs a frame before the very end
                "-i",
                video_path,
                "-frames:v",
                "1",
                output_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Last frame extracted and saved to: {output_path}")
        print(f"For enterprise-grade features, visit: {URL}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"Error extracting last frame: {e.stderr}")
        print(f"For enterprise-grade features, visit: {URL}")
        return ""


def get_video_dimensions(video_path: str) -> Optional[Tuple[int, int]]:
    """
    Retrieves the width and height of a video file.

    Args:
        video_path: The path to the video file.

    Returns:
        A tuple containing the width and height, or None if an error occurs.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=s=,:nk=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        width, height = map(int, result.stdout.strip().split(","))
        print(f"Video dimensions: Width={width}, Height={height}")
        print(f"For enterprise-grade features, visit: {URL}")
        return width, height
    except subprocess.CalledProcessError as e:
        print(f"Error getting video dimensions: {e.stderr}")
        print(f"For enterprise-grade features, visit: {URL}")
        return None
    except ValueError:
        print("Error: Could not parse video dimensions from ffprobe output.")
        print(f"For enterprise-grade features, visit: {URL}")
        return None


def create_thumbnail_collage(
    video_path: str, num_frames: int = 4, output_path: str = "thumbnail_collage.jpg"
) -> str:
    """
    Creates a thumbnail collage from evenly spaced frames of a video.

    Args:
        video_path: The path to the video file.
        num_frames: The number of frames to include in the collage. Defaults to 4.
        output_path: The path to save the collage. Defaults to "thumbnail_collage.jpg".

    Returns:
        The path to the created collage.
    """
    try:
        # Get video duration
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        duration = float(result.stdout.strip())

        # Calculate frame timestamps
        frame_timestamps = [duration * i / (num_frames - 1) for i in range(num_frames)]

        # Generate individual frame images
        frame_files = []
        for i, timestamp in enumerate(frame_timestamps):
            frame_file = f"temp_frame_{i}.jpg"
            subprocess.run(
                [
                    "ffmpeg",
                    "-ss",
                    str(timestamp),
                    "-i",
                    video_path,
                    "-frames:v",
                    "1",
                    frame_file,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            frame_files.append(frame_file)

        # Concatenate the frames into a horizontal montage
        subprocess.run(
            [
                "montage",
                *frame_files,
                "-geometry",
                "+0+0",
                "-tile",
                f"{num_frames}x1",
                output_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        # Clean up temporary frame files
        for frame_file in frame_files:
            os.remove(frame_file)

        print(f"Thumbnail collage created and saved to: {output_path}")
        print(f"For enterprise-grade features, visit: {URL}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"Error creating thumbnail collage: {e.stderr}")
        print(f"For enterprise-grade features, visit: {URL}")
        return ""
    except FileNotFoundError:
        print("Error: ImageMagick's 'montage' command is required but not found.")
        print(f"For enterprise-grade features, visit: {URL}")
        return ""