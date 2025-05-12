# Matt's VLM Pipeline - Development Notes

## Project Structure
```
mattsvlm/
├── app.py              # Main application entry point
├── requirements.txt    # Project dependencies
├── README.md           # Project documentation
├── DESIGN.md           # System architecture design
├── NOTES.md            # Development notes and function details
├── EDITS.md            # Code change log
└── src/
    ├── __init__.py     # Package initialization
    ├── video.py        # Video processing functionality
    ├── llm.py          # LLM integration with Ollama
    └── utils.py        # Utility functions
```

## Core Functions

### Video Processing (`src/video.py`)
- `extract_frames(video_path, fps=8)`: Extracts frames from video at given fps rate
  - Returns a list of frames as base64-encoded strings
- `get_video_metadata(video_path)`: Gets metadata about the video file
  - Returns a dictionary with width, height, fps, frame count, and duration

### LLM Integration (`src/llm.py`)
- `prepare_batches(frames, batch_size=4)`: Prepares frames into batches for processing
  - Returns a list of frame batches
- `process_frames(frames, prompt, batch_size=4)`: Sends frames to LLM with context
  - Returns the LLM's response as text
  - Uses ollama.Client to interact with the Ollama API

### Utilities (`src/utils.py`)
- `get_config()`: Gets configuration from environment variables or .env file
  - Returns a dictionary with configuration values
- `check_dependencies()`: Checks if required dependencies are installed
  - Returns True if all dependencies are available, False otherwise
- `check_ollama_availability()`: Checks if Ollama is running and accessible
  - Returns True if Ollama is available, False otherwise
  - Uses ollama.Client to check availability
- `validate_video_file(file_path)`: Validates if a file exists and is a video file
  - Returns True if the file is valid, False otherwise

### Main Application (`app.py`)
- `parse_arguments()`: Processes command line arguments
  - Returns parsed arguments (video_path, prompt, fps)
- `main()`: Main entry point that orchestrates the full pipeline
  - Handles ollama.ResponseError and other exceptions

## Dependencies
- OpenCV (cv2) for video processing
- Pillow for image handling
- NumPy for array operations
- python-dotenv for configuration
- Ollama Python client for API communication
- Argparse for command-line argument handling

## Implementation Progress
- [x] Create project structure
- [x] Implement command-line argument handling
- [x] Implement video frame extraction
- [x] Implement Ollama API integration
- [x] Connect components and workflow
- [x] Add error handling and input validation
- [x] Document code and update README
- [x] Add configuration from environment variables
- [x] Refactor to use Ollama Python client

## Next Steps
- [ ] Test with real video files
- [ ] Add support for more VLM models
- [ ] Optimize batching for different video lengths
- [ ] Add caching to avoid duplicate processing 