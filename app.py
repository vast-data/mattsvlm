#!/usr/bin/env python3
"""
Matt's VLM Pipeline

A tool for analyzing video clips using a Vision Language Model.
"""

import argparse
import sys
import os
import time
import ollama
from dotenv import load_dotenv
import pathlib
from src.video import extract_frames, get_video_metadata
from src.llm import process_frames
from src.utils import check_dependencies, check_ollama_availability, validate_video_file, get_config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process video clips with a Vision Language Model",
        prog="mattsvlm"
    )
    
    parser.add_argument(
        "video_file",
        help="Path to the video file (MP4/H264 format)"
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        default="summarize what is happening",
        help="Text prompt for the VLM (default: 'summarize what is happening')"
    )
    
    parser.add_argument(
        "-fps", "--frames-per-second",
        type=int,
        default=8,
        help="Frames per second to extract from video (default: 8)"
    )
    
    parser.add_argument(
        "-bs", "--batch-size",
        type=int,
        default=None,
        help="Maximum number of frames to process in each batch (default: auto-calculated)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    # Explicitly load .env from the script's directory parent (project root)
    script_dir = pathlib.Path(__file__).parent.resolve()
    dotenv_path = script_dir / ".env"
    load_dotenv(dotenv_path=dotenv_path)
    # Start tracking overall execution time
    start_time = time.time()
    
    # Check dependencies first
    if not check_dependencies():
        print("Error: Missing required dependencies. Please install them and try again.")
        sys.exit(1)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Get configuration
    config = get_config()
    
    # Validate video file
    if not validate_video_file(args.video_file):
        print(f"Error: '{args.video_file}' is not a valid video file or does not exist.")
        sys.exit(1)
    
    # Check if Ollama is available
    if not check_ollama_availability():
        print(f"Error: Ollama is not available. Please make sure it's running and accessible at {config['ollama_host']}.")
        sys.exit(1)
    
    try:
        # Get video metadata
        metadata = get_video_metadata(args.video_file)
        print(f"Video: {args.video_file}")
        print(f"Duration: {metadata['duration']:.2f}s, Resolution: {metadata['width']}x{metadata['height']}, FPS: {metadata['fps']:.2f}")
        print(f"Using Ollama at: {config['ollama_host']}")
        print(f"Using model: {config['ollama_model']} (128k context window)")
        
        if metadata['duration'] > 60:
            print(f"Error: Video duration ({metadata['duration']:.2f}s) exceeds maximum allowed (60s).")
            sys.exit(1)
        
        # Extract frames from video
        extraction_start = time.time()
        print(f"\n--- Extracting frames at {args.frames_per_second} fps... ---")
        frames = extract_frames(args.video_file, args.frames_per_second)
        extraction_time = time.time() - extraction_start
        print(f"Extracted {len(frames)} frames in {extraction_time:.2f} seconds.")
        
        # Process frames with VLM - let the system auto-calculate optimal batch size
        print(f"\n--- Analyzing frames with prompt: '{args.prompt}'... ---")
        result = process_frames(frames, args.prompt, batch_size=args.batch_size, fps=args.frames_per_second)
        
        # Split result from performance statistics if present
        if "--- Performance Statistics ---" in result:
            analysis_result, performance_stats = result.split("--- Performance Statistics ---", 1)
            
            # Output analysis result
            print("\nAnalysis Result:")
            print("-" * 80)
            print(analysis_result.strip())
            print("-" * 80)
            
            # Output performance stats
            print("\nPerformance Statistics:")
            print("-" * 80)
            print(f"--- Performance Statistics ---{performance_stats}")
            print("-" * 80)
        else:
            # Output the entire result if no statistics section is found
            print("\nAnalysis Result:")
            print("-" * 80)
            print(result)
            print("-" * 80)
        
        # Calculate and display total application runtime
        total_runtime = time.time() - start_time
        print(f"\nTotal application runtime: {total_runtime:.2f} seconds")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ollama.ResponseError as e:
        print(f"Ollama Error: {e.error} (Status: {e.status_code})")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 