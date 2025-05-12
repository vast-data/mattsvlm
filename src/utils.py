"""
Utility functions for the VLM pipeline.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration defaults
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llava:latest"
DEFAULT_ENDPOINT_TYPE = "ollama"
DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_OPENAI_BASE_URL = None # Default is to use official OpenAI URL
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_TOP_P = 1.0


def get_config():
    """
    Get configuration from environment variables or .env file.
    Validates required settings based on ENDPOINT_TYPE.
    
    Returns:
        dict: Configuration dictionary
    Raises:
        ValueError: If required configuration for the selected endpoint is missing.
    """
    config = {
        "endpoint_type": os.getenv("ENDPOINT_TYPE", DEFAULT_ENDPOINT_TYPE).lower(),
        "ollama_host": os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST),
        "ollama_model": os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        "openai_base_url": os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL),
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_LLM_TEMPERATURE)),
        "top_p": float(os.getenv("LLM_TOP_P", DEFAULT_LLM_TOP_P)),
    }

    # Validation based on endpoint type
    if config["endpoint_type"] == "openai":
        if not config["openai_api_key"] or config["openai_api_key"] == "YOUR_OPENAI_API_KEY":
            raise ValueError("ENDPOINT_TYPE is 'openai', but OPENAI_API_KEY is not set in environment or .env file.")
        if not config["openai_model"]:
            raise ValueError("ENDPOINT_TYPE is 'openai', but OPENAI_MODEL is not set.")
    elif config["endpoint_type"] == "ollama":
        if not config["ollama_host"]:
            raise ValueError("ENDPOINT_TYPE is 'ollama', but OLLAMA_HOST is not set.")
        if not config["ollama_model"]:
            raise ValueError("ENDPOINT_TYPE is 'ollama', but OLLAMA_MODEL is not set.")
    else:
        raise ValueError(f"Invalid ENDPOINT_TYPE: {config['endpoint_type']}. Must be 'ollama' or 'openai'.")

    return config


def check_dependencies():
    """
    Check if required dependencies are installed.
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    try:
        import cv2
        import numpy
        import requests
        from PIL import Image
        from dotenv import load_dotenv
        import ollama
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False


def check_ollama_availability():
    """
    Check if Ollama is running and available.
    Only runs if endpoint type is 'ollama'.
    
    Returns:
        bool: True if Ollama is available, False otherwise
    """
    import ollama
    
    config = get_config()
    if config["endpoint_type"] != "ollama":
        print("Endpoint type is not 'ollama', skipping Ollama availability check.")
        return True # Assume OK if not using Ollama
        
    ollama_host = config["ollama_host"]
    
    print(f"Checking Ollama availability at: {ollama_host}")
    
    try:
        # Create client with the configured host
        client = ollama.Client(host=ollama_host)
        
        # Debug: verify client settings
        client_opts = getattr(client, "_client", None)
        if client_opts and hasattr(client_opts, "base_url"):
            print(f"Client base URL: {client_opts.base_url}")
        
        # Check if Ollama is available by listing models
        models = client.list()
        print(f"Connected successfully to Ollama, found {len(models['models'])} models")
        return True
    except Exception as e:
        print(f"Failed to connect to Ollama at {ollama_host}: {e}")
        return False


def validate_video_file(file_path):
    """
    Validate if the file exists and is likely a video file.
    
    Args:
        file_path (str): Path to the video file
        
    Returns:
        bool: True if the file is valid, False otherwise
    """
    if not os.path.isfile(file_path):
        return False
    
    # Check file extension
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    _, ext = os.path.splitext(file_path)
    
    return ext.lower() in valid_extensions 