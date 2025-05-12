"""
Video processing module for extracting frames from videos.
"""

import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image


def extract_frames(video_path, fps=8):
    """
    Extract frames from the video at the specified fps rate.
    
    Args:
        video_path (str): Path to the video file
        fps (int, optional): Frames per second to extract. Defaults to 8.
        
    Returns:
        list: List of frames as base64-encoded strings
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / video_fps
    
    # Calculate frame interval for desired fps
    frame_interval = int(video_fps / fps)
    
    # Check if the video is too long (more than 60 seconds)
    if duration > 60:
        raise ValueError(f"Video duration ({duration:.2f}s) exceeds maximum allowed (60s)")
    
    frames = []
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Only process frames at the desired interval
        if frame_number % frame_interval == 0:
            # Convert from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to base64 for the API
            pil_img = Image.fromarray(rgb_frame)
            buffer = BytesIO()
            pil_img.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            frames.append(img_str)
        
        frame_number += 1
    
    # Release the video capture object
    cap.release()
    
    if not frames:
        raise ValueError("No frames were extracted from the video")
    
    return frames


def get_video_metadata(video_path):
    """
    Get metadata for the video file.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        dict: Dictionary containing video metadata
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    # Release the video capture object
    cap.release()
    
    return {
        "width": width,
        "height": height,
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration
    } 