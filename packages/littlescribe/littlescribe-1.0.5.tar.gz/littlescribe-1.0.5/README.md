# AI Little Scribe
<p align="center">
<img src="logo.png" alt="AI Little Scribe Logo" width="200">
</p>

Real-time audio transcription tool that captures both system audio and microphone input, with AI-powered summarization.

## Features

- Real-time transcription of system audio + microphone
- Multi-language support
- AI-powered summary generation using Amazon Bedrock Nova Pro
- Configurable output files
- Speaker identification

## Prerequisites

- macOS 14.2+ with AudioTee binary installed
- AWS credentials configured
- Python 3.7+

## Installation

```bash
git clone https://gitlab.aws.dev/ndeplace/AI-LittleScribe.git
cd AI-LittleScribe
chmod +x install.sh install_audiotee.sh
./install.sh
```

This will:
1. Install AudioTee binary for system audio capture
2. Install Python dependencies
3. Compile the script into a standalone binary
4. Install the binary to `/usr/local/bin/littlescribe`

## Usage

### With uvx (recommended - no installation needed)

```bash
# System audio only (default)
uvx littlescribe

# Microphone only
uvx littlescribe --microphone

# Both system audio + microphone
uvx littlescribe --both

# With custom options
uvx littlescribe --language fr-FR --output meeting.txt --summary summary.txt
```

### Local installation

```bash
git clone https://gitlab.aws.dev/ndeplace/AI-LittleScribe.git
cd AI-LittleScribe
chmod +x install.sh install_audiotee.sh
./install.sh
```

Then run:
```bash
# Basic usage (English)
littlescribe

# French transcription
littlescribe --language fr-FR

# Custom output with summary
littlescribe --output meeting.txt --summary meeting_summary.txt
```

## Parameters

- `--language, -l`: Input language code (default: en-US)
- `--output, -o`: Output file (default: transcription_output.txt)  
- `--summary, -s`: Summary output file (optional)
- `--microphone, -m`: Record microphone instead of system audio
- `--both, -b`: Record both microphone and system audio

Press Ctrl+C to stop recording and generate summary.

## Local development

Run

```bash
$ uv run python -m littlescribe
```
