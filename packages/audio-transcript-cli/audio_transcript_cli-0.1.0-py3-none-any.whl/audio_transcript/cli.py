import argparse
import sys
import os
from .core import transcribe

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI Whisper.")
    parser.add_argument("input_file", help="Path to the input audio file (MP3, WAV, etc.)")
    parser.add_argument("--model", default="openai/whisper-large-v2", help="Whisper model name (default: openai/whisper-large-v2)")
    parser.add_argument("--chunk-size", type=int, default=30000, help="Chunk length in milliseconds (default: 30000)")
    parser.add_argument("--device", help="Device to use (cuda, cpu, mps). Auto-detected if not provided.")
    parser.add_argument("-o", "--output", default="transcript.txt", help="Output text file path (default: transcript.txt)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
        
    try:
        print(f"Starting transcription for {args.input_file}...")
        transcript = transcribe(
            audio_path=args.input_file,
            model_name=args.model,
            chunk_length_ms=args.chunk_size,
            device=args.device
        )
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(transcript)
            
        print(f"\nSuccess! Transcript saved to '{args.output}'")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
