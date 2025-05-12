# Matt's VLM Pipeline Design

## Overview
A standalone Python module for processing video clips (up to 1 minute in length) and analyzing them with a Vision Language Model via Ollama.

## Components
1. **Command-Line Interface**
   - Process input arguments (video file, prompt, fps)
   - Handle input validation

2. **Video Processing**
   - Extract frames from video at specified fps
   - Convert frames to appropriate format for VLM

3. **VLM Integration**
   - Send frames to Ollama (using gemma3 model)
   - Include prompt and context with frames
   - Process response from model

## Data Flow
1. User inputs video file and optional prompt/fps
2. System extracts frames at specified rate
3. Frames and prompt are sent to VLM
4. VLM response is returned to the console

## Technical Constraints
- Keep dependencies minimal
- Focus on core functionality
- Ensure proper error handling
- Support MP4/H264 video format
- Default fps: 8
- Default prompt: "summarize what is happening" 