# FFmpegTools

![FFmpegTools Banner](assets/banner.png)

A lightweight collection of Windows batch scripts that simplify common media processing tasks using FFmpeg. Designed for quick and efficient video conversion and audio extraction without requiring command-line interaction.

---

## Overview

FFmpegTools provides simple drag-and-drop utilities for common media processing workflows. By leveraging the power of FFmpeg behind an easy-to-use interface, users can convert videos, create high-quality GIFs, and extract audio with minimal effort.

Whether you need to standardize video formats, generate GIFs for documentation or social media, or extract high-quality audio from media files, FFmpegTools offers a straightforward solution for everyday tasks.

> **Note:** FFmpeg must be installed and available in the system PATH before using these utilities.

---

## Features

- Convert video files to MP4 format
- Convert MP4 videos to high-quality GIFs
- Preserve original resolution and frame rate when creating GIFs
- Extract audio from video files as WAV
- Simple drag-and-drop workflow
- Supports multiple files via drag-and-drop
- Automatically saves output beside the original file
- No manual FFmpeg commands required
- Lightweight and portable
- Fast and efficient processing

---

## Included Utilities

### VideoToMP4.bat

Converts supported video files into MP4 format for improved compatibility across devices and platforms.

### VideoToGif.bat

Creates high-quality animated GIFs from MP4 videos using FFmpeg's two-pass palette generation for optimal color accuracy.

**Highlights**

- Preserves the original frame rate (FPS)
- Preserves the original resolution
- Uses palette generation for maximum GIF quality
- Automatically removes temporary files
- Saves the GIF in the same folder as the source video
- Supports dragging multiple MP4 files at once

### VideoToWav.bat

Extracts audio from video files and saves it as an uncompressed WAV file suitable for editing, processing, or archival purposes.

---

## Repository Structure

```text
FFmpegTools/
│
├── VideoToMP4.bat
├── VideoToGif.bat
├── VideoToWav.bat
├── README.md
│
└── Assets/
    └── Banner.png
```

---

## Requirements

FFmpegTools requires FFmpeg to be installed on your system.

### Install FFmpeg

1. Download FFmpeg from the official website:
   https://ffmpeg.org/download.html

2. Extract the downloaded files.

3. Add the FFmpeg `bin` folder to your system PATH.

4. Verify the installation by opening Command Prompt and running:

```bash
ffmpeg -version
```

If FFmpeg is installed correctly, version information will be displayed.

---

## Usage

### Convert a Video to MP4

1. Drag and drop a video file onto `VideoToMP4.bat`
2. Wait for processing to complete
3. The converted MP4 file will be generated automatically

---

### Convert MP4 to GIF

1. Drag and drop one or more MP4 files onto `VideoToGif.bat`
2. Wait for processing to complete
3. A high-quality GIF will be generated beside each original MP4 file

---

### Extract Audio as WAV

1. Drag and drop a video file onto `VideoToWav.bat`
2. Wait for processing to complete
3. The extracted WAV file will be generated automatically

---

## Applications

- Video format standardization
- High-quality GIF creation
- README and GitHub documentation
- Screen recording conversion
- Social media content creation
- Audio extraction from media files
- Content creation workflows
- Media archiving
- Educational and personal projects
- Quick file conversion without command-line usage

---

## Technologies Used

- Windows Batch Scripting
- FFmpeg
- Windows Command Line Utilities

---

## Future Enhancements

Potential improvements that may be added in future versions:

- Support for additional output formats
- Adjustable GIF quality and scaling options
- Compression and optimization presets
- Batch folder processing
- Custom output directory selection
- Graphical User Interface (GUI)
- Logging and processing reports

---

## Contributing & Feedback

Suggestions, ideas, feature requests, and improvements are always welcome.

If you have an idea for enhancing FFmpegTools, discover a bug, or want to contribute new functionality, feel free to open an issue or submit a pull request.

Community feedback helps make the project more useful and reliable for everyone.

---

## Author

Developed and maintained by **K Nithin Kumar Goud**.

Bachelor of Engineering, Electronics and Communication Engineering (ECE).

---

⭐ If you found this project useful, consider giving the repository a star.