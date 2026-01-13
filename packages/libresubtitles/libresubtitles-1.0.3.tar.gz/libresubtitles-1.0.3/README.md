# LibreSubtitles

![PyPI](https://img.shields.io/pypi/v/libresubtitles)
![License](https://img.shields.io/badge/License-Apache%202.0-blue)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)

**LibreSubtitles** is an open-source, offline subtitle generator accurate subtitles using [Whisper](https://github.com/openai/whisper). 

---
![Project Logo](https://raw.githubusercontent.com/chirag-juneja/LibreSubtitles/refs/heads/master/assets/logo.png) 
---
## Features

- Generate `.srt` subtitles from audio or video files.
- Works offline; privacy-first.
- Handles long videos efficiently by splitting on silence.
- CLI interface for quick usage.
- Cross-platform: Linux, macOS, Windows (CPU mode recommended).  

---

## Requirements

- Python 3.13 or higher
- [FFmpeg](https://ffmpeg.org/) installed and accessible from your `PATH`


## Installation

Install via pip:

```bash
pip install libresubtitles
```

## Usage

```bash
libresubtitles -i /path/to/video.mp4
```
