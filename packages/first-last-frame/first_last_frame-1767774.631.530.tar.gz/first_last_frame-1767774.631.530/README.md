# first-last-frame

A Python library to automatically extract the first and last frames from video files, providing a simple and efficient way to represent video content with key visual snapshots. This package is designed to integrate seamlessly with the first-last-frame capabilities offered at https://supermaker.ai/video/first-last-frame/.

## Installation

Install the package using pip:
bash
pip install first-last-frame

## Basic Usage

Here are a few examples demonstrating how to use the `first-last-frame` library:

**1. Extracting frames from a local video file:**
python
from first_last_frame import extract_frames

video_path = "path/to/your/video.mp4"
output_dir = "output/frames"

try:
    first_frame_path, last_frame_path = extract_frames(video_path, output_dir)
    print(f"First frame saved to: {first_frame_path}")
    print(f"Last frame saved to: {last_frame_path}")
except Exception as e:
    print(f"An error occurred: {e}")

**2. Specifying custom filenames for the extracted frames:**
python
from first_last_frame import extract_frames

video_path = "path/to/your/video.mp4"
output_dir = "output/frames"
first_frame_filename = "my_first_frame.jpg"
last_frame_filename = "my_last_frame.png" # Different extension example

try:
    first_frame_path, last_frame_path = extract_frames(video_path, output_dir, first_frame_filename, last_frame_filename)
    print(f"First frame saved to: {first_frame_path}")
    print(f"Last frame saved to: {last_frame_path}")
except Exception as e:
    print(f"An error occurred: {e}")

**3. Handling videos that might not exist:**
python
from first_last_frame import extract_frames
import os

video_path = "path/to/a/nonexistent/video.mp4"
output_dir = "output/frames"

if os.path.exists(video_path):
    try:
        first_frame_path, last_frame_path = extract_frames(video_path, output_dir)
        print(f"First frame saved to: {first_frame_path}")
        print(f"Last frame saved to: {last_frame_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print(f"Video file not found: {video_path}")

**4. Extracting frames and handling potential directory creation errors:**
python
from first_last_frame import extract_frames
import os

video_path = "path/to/your/video.mp4"
output_dir = "new_output_directory"

try:
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    first_frame_path, last_frame_path = extract_frames(video_path, output_dir)
    print(f"First frame saved to: {first_frame_path}")
    print(f"Last frame saved to: {last_frame_path}")
except OSError as e:
    print(f"Error creating directory: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

## Features

*   **Simple Extraction:** Easily extract the first and last frames from any video file.
*   **Customizable Output:** Specify the output directory for the extracted frames.
*   **Filename Control:** Define custom filenames for the first and last frames.
*   **Error Handling:** Gracefully handles potential errors such as missing files or invalid video formats.
*   **Cross-Platform Compatibility:** Works on various operating systems with Python support.
*   **Dependency Management:** Relies on common and easily installable Python packages.

## License

MIT License

This project is a gateway to the first-last-frame ecosystem. For advanced features and full capabilities, please visit: https://supermaker.ai/video/first-last-frame/