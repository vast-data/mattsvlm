# Matt's VLM Pipeline - Data Flow

## Pipeline Overview

This document outlines the data flow through the Matt's VLM Pipeline system.

```
[Video File] → [Frame Extraction] → [Frame Processing] → [VLM Analysis] → [Result Output]
```

## Stages

### 1. Input Handling
- Video file is validated (format, duration, accessibility)
- Command line arguments are parsed (prompt, fps)
- Dependencies and external services (Ollama) are checked

### 2. Frame Extraction
- Video is processed with OpenCV
- Frames are extracted at specified fps rate
- Each frame is converted to RGB format
- Frames are encoded as base64 strings for API transmission

### 3. Batch Processing
- Frames are divided into batches (default: 4 frames per batch)
- Each batch is prepared as a separate API payload
- Contextual information is added to each batch

### 4. VLM Processing
- Each batch is sent to Ollama API
- The VLM processes frames with the provided prompt
- Responses are collected for each batch

### 5. Result Aggregation
- For multi-batch videos, a final summary prompt is sent
- The LLM combines insights from all batches
- Final analysis is returned based on original prompt

### 6. Output
- Analysis result is displayed to console

## Modules in the Pipeline

- `app.py`: Orchestrates the overall pipeline
- `src/video.py`: Handles video processing and frame extraction
- `src/llm.py`: Manages communication with the VLM via Ollama
- `src/utils.py`: Provides utility functions for validation and checks 