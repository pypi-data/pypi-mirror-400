# Audio Transcript CLI

[![PyPI version](https://img.shields.io/pypi/v/audio-transcript-cli.svg)](https://pypi.org/project/audio-transcript-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust Python tool to transcribe large audio files (MP3, WAV, M4A, etc.) using OpenAI's Whisper model. 
It automatically chunks long audio files to avoid memory issues, making it perfect for transcribing long meetings, podcasts, or lectures on consumer hardware or Google Colab.

## Features

- **Automatic Chunking**: Splits large audio files into 30-second segments (customizable) to prevent OOM errors.
- **GPU Acceleration**: Automatically utilizes CUDA or MPS (Apple Silicon) if available.
- **Format Support**: Supports all audio formats compatiable with `ffmpeg` (MP3, WAV, M4A, FLAC, etc.) at 16kHz.
- **Easy CLI**: Simple command-line interface for quick usage.
- **Python API**: Importable functions for integration into your own Python scripts.

## Installation

You can install the package directly via pip:

```bash
pip install audio-transcript-cli
```

### System Requirements

This package requires **FFmpeg** to process audio files.

- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **Windows**: [Download FFmpeg](https://ffmpeg.org/download.html) and add to PATH.

## Usage

### Command Line Interface

Transcribe a file directly from your terminal:

```bash
transcribe-audio path/to/audio/meeting.mp3
```

**Options:**

| Flag | Description | Default |
|------|-------------|---------|
| `--model` | Whisper model size (`tiny`, `base`, `small`, `medium`, `large`, `large-v2`) | `openai/whisper-large-v2` |
| `--device` | Device to run on (`cuda`, `cpu`, `mps`). Auto-detected. | Auto |
| `--chunk-size` | Chunk length in milliseconds. | `30000` (30s) |
| `--output`, `-o` | Output text filename. | `transcript.txt` |

**Example:**
```bash
transcribe-audio podcast.mp3 --model openai/whisper-medium -o podcast_transcript.txt
# Supports M4A files too
transcribe-audio voice_note.m4a --model openai/whisper-base
```

### Python API

Use the transcriber in your own code:

```python
from audio_transcript import transcribe

# Transcribe a file
result = transcribe(
    audio_path="interview.mp3",
    model_name="openai/whisper-medium",
    chunk_length_ms=30000,
    device="cuda" # or "cpu", "mps"
)

print(result)

# Save to file
with open("transcript.txt", "w") as f:
    f.write(result)
```

## Running on Google Colab

Use the following commands in a Colab notebook cell to run the transcriber:

```python
# 1. Install system dependencies and the package
!apt-get install -y ffmpeg
!pip install git+https://github.com/azmatsiddique/audio-transcript-cli.git

# 2. Upload your file (drag and drop to the file pane on the left)

# 3. Running transcription
!transcribe-audio "your_file.mp3" --output "transcript.txt" --device cuda
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

**Azmat Siddique**  
Email: azmat.siddique.98@gmail.com
GitHub: [azmatsiddique](https://github.com/azmatsiddique)
