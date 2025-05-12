# Matt's VLM Pipeline - Code Changes Log

## 2024-04-02
- Created project structure
- Created DESIGN.md with system architecture
- Created NOTES.md with function definitions and implementation plan
- Created EDITS.md to track code changes
- Created app.py with command-line argument handling
- Created src/ directory with module structure
- Implemented video.py with frame extraction functionality
- Implemented llm.py with Ollama API integration
- Implemented utils.py with helper functions
- Added requirements.txt with dependencies
- Updated README.md with installation and usage instructions

### Implementation Details
- Video processing using OpenCV
- Base64 encoding of frames for API transmission
- Batching of frames to handle API limitations
- Error handling for various failure scenarios
- Input validation for video files
- Support for custom fps and prompts

### Code Structure
- Modular design with separate concerns (video, LLM, utils)
- Main app.py orchestrates the pipeline
- Clear error handling and user feedback
- Documentation throughout the codebase

## 2024-04-03
- Added configuration from environment variables and .env file
- Added support for custom Ollama host and model
- Added dotenv dependency
- Added sample .env.example file
- Updated documentation in USAGE.md
- Improved error messages to include configured host

### Configuration Options
- OLLAMA_HOST: URL for the Ollama server
- OLLAMA_MODEL: Model to use for video analysis

## 2024-04-04
- Refactored to use the official Ollama Python client library
- Replaced direct API calls with client methods in llm.py
- Updated utils.py to use the client for availability checks
- Added specific error handling for Ollama client errors in app.py
- Updated requirements.txt to include ollama package
- Removed temporary direct HTTP implementation (no longer needed)
- Simplified .env.example file
- Updated README.md to remove references to alternative implementation

### Benefits of Using Ollama Python Client
- More robust error handling
- Simplified code for API interactions
- Better type safety and response handling
- Direct support from the Ollama team
- Automatic handling of API versioning

## 2024-04-05
- Added detailed output for each batch processing step
- Implemented performance tracking and runtime statistics
- Enhanced console output with timing information
- Added separation of analysis results and performance data
- Improved visual formatting of console output

### Performance Metrics Tracked
- Total application runtime
- Frame extraction time
- Individual batch processing times
- Average time per batch
- Summary generation time
- Overall LLM processing time

## 2024-04-06
- Implemented improved temporal alignment for video frame analysis
- Added single-batch processing for optimal temporal understanding when possible
- Created overlapping batches technique to maintain continuity between frames
- Enhanced prompts with explicit temporal context and frame timestamps
- Passed previous batch observations to each subsequent batch for continuity
- Improved final summary to emphasize motion and change detection
- Added frame timestamps and time ranges to each batch

### Temporal Alignment Features
- Frames processed in order with temporal metadata
- Overlapping frames between batches for continuity
- Clear frame numbering and timestamps for context
- Previous observations carried forward
- Single-batch processing when few enough frames
- Explicit instructions for motion detection
- Enhanced summary generation with temporal focus

## 2024-04-07
- Optimized for 128k token context window by using much larger batch sizes
- Implemented automatic batch size calculation based on number of frames
- Increased default batch size from 4 to 32 frames per batch
- Added command-line option to manually specify batch size
- Enhanced context prompts to emphasize the larger temporal window
- Modified processing approach to use larger non-overlapping batches
- Improved performance by reducing the number of API calls

### Large Batch Size Benefits
- Better temporal understanding with more frames per batch
- Reduced number of API calls and overhead
- More efficient use of the large 128k context window
- Automatic optimization based on video length and content
- Improved motion detection with more frames visible at once
- Option to process entire video in a single batch when possible
- More detailed segment-by-segment analysis

### Next Improvements
- Add tests
- Support more VLM models
- Implement caching of processed frames
- Add progress indicators for long-running operations 