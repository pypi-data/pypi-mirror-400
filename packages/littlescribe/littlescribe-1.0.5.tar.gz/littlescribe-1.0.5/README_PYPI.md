# AI Little Scribe

Real-time audio transcription tool that captures both system audio and microphone input, with AI-powered summarization using Amazon Bedrock.

## Features

- Real-time transcription of system audio + microphone
- Multi-language support
- AI-powered summary generation
- Speaker identification
- Cross-platform support

## Prerequisites

- macOS 14.2+ with AudioTee binary
- AWS credentials configured
- Python 3.7+

## Installation & Usage

No installation needed! Use with uvx:

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

## Setup AudioTee (macOS only)

```bash
git clone https://github.com/makeusabrew/audiotee.git
cd audiotee && make && sudo cp audiotee /usr/local/bin/
```

## Parameters

- `--language, -l`: Input language code (default: en-US)
- `--output, -o`: Output file (default: transcription_output.txt)  
- `--summary, -s`: Summary output file (optional)
- `--microphone, -m`: Record microphone instead of system audio
- `--both, -b`: Record both microphone and system audio

Press Ctrl+C to stop recording and generate summary.

## AWS Setup

Configure AWS credentials via AWS CLI or environment variables:
```bash
aws configure
```

Requires access to Amazon Transcribe and Amazon Bedrock services.

## Important Notice

This tool uses AWS services (Amazon Transcribe for speech-to-text and Amazon Bedrock Nova Pro for AI summarization) which may incur charges to your AWS account. Please review AWS pricing for these services before use:

- [Amazon Transcribe Pricing](https://aws.amazon.com/transcribe/pricing/)
- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

You are responsible for any AWS charges incurred while using this tool.
