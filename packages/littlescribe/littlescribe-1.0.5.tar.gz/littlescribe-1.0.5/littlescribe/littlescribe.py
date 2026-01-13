#!/usr/bin/env python3
import asyncio
import subprocess
import struct
import argparse
import boto3
import json
import os
import shutil
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from datetime import datetime
import logging


logger = logging.getLogger(__name__)

# Set AWS region and credentials explicitly
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')

def check_dependencies(use_microphone=False, use_both=False):
    """Check if required system dependencies are available."""
    missing_deps = []
    
    if not shutil.which('audiotee'):
        missing_deps.append(("AudioTee", "git clone https://github.com/makeusabrew/audiotee.git && cd audiotee && make && sudo cp audiotee /usr/local/bin/"))
    
    if (use_microphone or use_both) and not shutil.which('ffmpeg'):
        missing_deps.append(("ffmpeg", "brew install ffmpeg"))
    
    if missing_deps:
        print("Error: Missing required dependencies:")
        for dep_name, install_cmd in missing_deps:
            print(f"  {dep_name}: {install_cmd}")
        return False
    
    return True

CHUNK_SIZE = 1024 * 2
SAMPLE_RATE = 16000

class FileTranscriptHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, output_file):
        super().__init__(output_stream)
        self.output_file = output_file
        self.transcript_text = []
        self.last_speaker = None
        
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        for result in transcript_event.transcript.results:
            if not result.is_partial:
                for alt in result.alternatives:
                    text = alt.transcript.strip()
                    if text:
                        speaker = "Unknown"
                        if hasattr(alt, 'items') and alt.items:
                            for item in alt.items:
                                if hasattr(item, 'speaker') and item.speaker:
                                    speaker = item.speaker
                                    break
                        
                        # Add bold formatting for speaker changes
                        speaker_change_marker = ""
                        if self.last_speaker and self.last_speaker != speaker:
                            speaker_change_marker = "**[SPEAKER CHANGE]** "
                        self.last_speaker = speaker
                        
                        line = f"{speaker}: {speaker_change_marker}{text}\n"
                        print(line.strip())
                        with open(self.output_file, 'a') as f:
                            f.write(line)
                        self.transcript_text.append(text)
            # Skip partial results

async def mixed_audio_generator():
    try:
        # Start AudioTee for system audio
        process = subprocess.Popen(
            ['audiotee', '--sample-rate', str(SAMPLE_RATE)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("Recording system audio...")
        
        import numpy as np
        
        while True:
            chunk = process.stdout.read(CHUNK_SIZE * 2)
            if not chunk:
                break
            
            # Amplify system audio by 2x
            audio_data = np.frombuffer(chunk, dtype=np.int16)
            amplified = np.clip(audio_data.astype(np.int32) * 2, -32768, 32767).astype(np.int16)
            yield amplified.tobytes()
            
            await asyncio.sleep(0.01)
            
    except FileNotFoundError:
        logger.error("AudioTee not found. Please install AudioTee.")
        raise
    except Exception as e:
        logger.error(f"Audio capture error: {e}")
        raise
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait()

def generate_summary(transcript_text, output_file=None):
    if not transcript_text:
        return
    
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    system_prompt = """Can you format this meeting note. Try to structure in the most logical way. DO NOT remove information. DO NOT add content or hallucinate. I am just asking to format on a proper structure and improve wording.

- This is a audio transcript - there might be odd words because the transcritpion is not correct. Don't take too importance on each statement and try to understand the context to guess the meaning of something abnormal.  
- When not sure about the meaning of a statement, you can remove it unless you are sure to understand what it means
- Write the note in english even if it's written in french.
- There might be acronyms not well transcribes. This are a few we often see: AWS, DoiT, k (for thousands), AI, VC (venture capital), BD (Business developer), SA (solution architect) 
- Avoid too many bullet points. Use it for main categories and paragraph, but then try writing short and clear sentences.
- DO NOT HALLUCINATE. You must use only content provided in the context. If you haven't got enough data, adapt the structure format. You can even say one sentence.
- DO NOT start by an introduction like "Here's the formatted meeting note", instead start with the summary directly.
"""
    
    transcript = ' '.join(transcript_text)
    
    payload = {
        "messages": [
            {"role": "user", "content": [{"text": f"<context>Meeting transcription</context>\n\n{transcript}"}]}
        ],
        "system": [{"text": system_prompt}],
        "inferenceConfig": {
            "maxTokens": 10000,
            "temperature": 0.3
        }
    }
    
    try:
        response = bedrock.invoke_model(
            modelId='amazon.nova-pro-v1:0',
            body=json.dumps(payload)
        )
        
        result = json.loads(response['body'].read())
        summary = result['output']['message']['content'][0]['text']
        
        print(f"\n--- MEETING SUMMARY ---\n{summary}\n")
        
        if output_file:
            with open(output_file, 'a') as f:
                f.write(f"\n--- MEETING SUMMARY ---\n{summary}\n")
    except Exception as e:
        print(f"Summary generation failed: {e}")

async def microphone_audio_generator():
    try:
        process = subprocess.Popen([
            'ffmpeg', '-f', 'avfoundation', '-i', ':1',  # External Microphone
            '-ar', str(SAMPLE_RATE), '-ac', '1', '-f', 's16le', '-'
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        print("Recording microphone...")
        
        while True:
            chunk = process.stdout.read(CHUNK_SIZE * 2)
            if not chunk:
                break
            yield chunk
            await asyncio.sleep(0.01)
            
    except Exception as e:
        logger.error(f"Microphone error: {e}")
        raise
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait()

async def both_audio_generator():
    try:
        # Start AudioTee for system audio
        system_process = subprocess.Popen(
            ['audiotee', '--sample-rate', str(SAMPLE_RATE)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Start microphone recording
        mic_process = subprocess.Popen([
            'ffmpeg', '-f', 'avfoundation', '-i', ':1',  # External Microphone
            '-ar', str(SAMPLE_RATE), '-ac', '1', '-f', 's16le', '-'
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        print("Recording system audio + microphone with speaker separation...")
        
        import numpy as np
        
        last_dominant = None  # Track which source was dominant
        silence_chunk = np.zeros(CHUNK_SIZE, dtype=np.int16).tobytes()
        
        while True:
            system_chunk = system_process.stdout.read(CHUNK_SIZE * 2)
            mic_chunk = mic_process.stdout.read(CHUNK_SIZE * 2)
            
            if not system_chunk and not mic_chunk:
                break
                
            # Mix audio if both chunks are available
            if len(system_chunk) == len(mic_chunk) == CHUNK_SIZE * 2:
                system_audio = np.frombuffer(system_chunk, dtype=np.int16)
                mic_audio = np.frombuffer(mic_chunk, dtype=np.int16)
                
                # Calculate RMS levels to determine dominant source
                system_rms = np.sqrt(np.mean(system_audio.astype(np.float32) ** 2))
                mic_rms = np.sqrt(np.mean(mic_audio.astype(np.float32) ** 2))
                
                # Determine current dominant source (with threshold to avoid noise)
                current_dominant = None
                if system_rms > 100:  # System audio threshold
                    current_dominant = 'system'
                elif mic_rms > 20:   # Lower microphone threshold for earlier detection
                    current_dominant = 'mic'
                
                # If dominant source changed, inject silence to force speaker boundary
                if current_dominant and last_dominant and current_dominant != last_dominant:
                    # Send 0.5 seconds of silence (8000 samples / 1024 per chunk = ~8 chunks)
                    for _ in range(8):
                        yield silence_chunk
                        await asyncio.sleep(0.01)
                
                if current_dominant:
                    last_dominant = current_dominant
                
                # Amplify microphone by 3x and mix
                mic_amplified = np.clip(mic_audio.astype(np.int32) * 3, -32768, 32767)
                mixed_audio = ((system_audio.astype(np.int32) + mic_amplified) // 2).astype(np.int16)
                yield mixed_audio.tobytes()
            elif system_chunk:
                yield system_chunk
            elif mic_chunk:
                yield mic_chunk
                
            await asyncio.sleep(0.01)
            
    except Exception as e:
        logger.error(f"Both audio error: {e}")
        raise
    finally:
        if 'system_process' in locals():
            system_process.terminate()
            system_process.wait()
        if 'mic_process' in locals():
            mic_process.terminate()
            mic_process.wait()

async def start_transcription(language_code, output_file, summary_output, use_microphone=False, use_both=False):
    print(f"Starting transcription in {language_code}... Output: {output_file}")
    print("Press Ctrl+C to stop\n")
    
    with open(output_file, 'w') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Transcription started\n\n")
    
    stream_transcription = None
    handler = None
    
    try:
        # Get credentials from boto3 session
        session = boto3.Session()
        creds = session.get_credentials()
        
        if creds is None:
            raise Exception("AWS credentials not found. Please run 'aws configure' or 'mwinit' or 'insengardcli assume'")
        
        # Set environment variables for amazon-transcribe
        os.environ['AWS_ACCESS_KEY_ID'] = creds.access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = creds.secret_key
        if creds.token:
            os.environ['AWS_SESSION_TOKEN'] = creds.token
        
        client = TranscribeStreamingClient(region="us-east-1")
        
        stream_transcription = await client.start_stream_transcription(
            language_code=language_code,
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm",
            show_speaker_label=True,
        )
        
        handler = FileTranscriptHandler(stream_transcription.output_stream, output_file)
        
        async def send_audio():
            try:
                # Use appropriate audio generator
                if use_both:
                    audio_gen = both_audio_generator()
                elif use_microphone:
                    audio_gen = microphone_audio_generator()
                else:
                    audio_gen = mixed_audio_generator()
                    
                async for chunk in audio_gen:
                    if not chunk:
                        break
                    
                    # Always send chunks to prevent timeout, but log when we get real audio
                    if any(b != 0 for b in chunk):
                        pass  # Silent audio detection
                    
                    await stream_transcription.input_stream.send_audio_event(audio_chunk=chunk)
                    await asyncio.sleep(0.01)
                    
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Audio streaming error: {e}")
        
        await asyncio.gather(send_audio(), handler.handle_events())
        
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nTranscription stopped by user")
    finally:
        if stream_transcription:
            try:
                await stream_transcription.input_stream.end_stream()
            except:
                pass
        if handler and handler.transcript_text:
            generate_summary(handler.transcript_text, summary_output)

def main():
    parser = argparse.ArgumentParser(description='AI Little Scribe - Audio Transcription Tool')
    parser.add_argument('--language', '-l', default='en-US', help='Input language code (default: en-US)')
    parser.add_argument('--output', '-o', default='transcription_output.txt', help='Output file (default: transcription_output.txt)')
    parser.add_argument('--summary', '-s', help='Summary output file (optional)')
    parser.add_argument('--microphone', '-m', action='store_true', help='Record microphone instead of system audio')
    parser.add_argument('--both', '-b', action='store_true', help='Record both microphone and system audio')
    
    args = parser.parse_args()
    
    if not check_dependencies(args.microphone, args.both):
        return 1
        
    asyncio.run(start_transcription(args.language, args.output, args.summary, args.microphone, args.both))

if __name__ == "__main__":
    logger.info("Starting LittleScribe")
    main()
