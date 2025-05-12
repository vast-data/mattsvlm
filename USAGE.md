# Matt's VLM Pipeline - Usage Guide

## Installation

1. Ensure you have Python 3.8+ installed
2. Install Ollama from [https://ollama.ai/](https://ollama.ai/)
3. Pull the gemma3 model in Ollama: `ollama pull gemma3` (or any other model you want to use)
4. Install dependencies: `pip install -r requirements.txt`
5. (Optional) Create a `.env` file to configure the Ollama host and model (see Configuration section)

## Configuration

You can configure the Ollama host and model using environment variables or a `.env` file in the project root.

Available configuration options:
- `OLLAMA_HOST`: URL for the Ollama server (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Model to use for analysis (default: `gemma3`)

Example `.env` file:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3
```

For a remote Ollama server or a different model:
```
OLLAMA_HOST=http://your-ollama-server:11434
OLLAMA_MODEL=llava
```

## Basic Usage

The simplest way to use Matt's VLM Pipeline:

```bash
python app.py path/to/video.mp4
```

This will:
- Extract frames at 8 frames per second
- Send them to the configured model via Ollama
- Generate a summary of what's happening in the video

## Command Line Options

```bash
python app.py VIDEO_FILE [PROMPT] [-fps FRAMES_PER_SECOND]
```

### Parameters:

- `VIDEO_FILE`: Path to the MP4/H264 video file (required)
- `PROMPT`: Text prompt for the VLM (optional, default: "summarize what is happening")
- `-fps`, `--frames-per-second`: Number of frames per second to extract (optional, default: 8)

## Examples

### Basic Summary
```bash
python app.py vacation.mp4
```

### Object Detection
```bash
python app.py street_scene.mp4 "list all vehicles visible in the video"
```

### Character Description
```bash
python app.py movie_clip.mp4 "describe the main character's appearance and actions" -fps 12
```

### Scene Analysis
```bash
python app.py nature_video.mp4 "identify all wildlife species and their behaviors"
```

## Tips

- Higher fps values will result in more detailed analysis but slower processing
- Keep videos under 60 seconds in length
- For best results, ensure Ollama has enough resources allocated
- Specific, focused prompts usually produce better results than vague ones
- If you're using a remote Ollama server, ensure it has the specified model installed 