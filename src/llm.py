"""
LLM integration module for interacting with Ollama or OpenAI VLM endpoints.
"""

import time
import base64 # Added for OpenAI image handling
import os     # Added for OpenAI API key
import ollama
import openai # Added OpenAI client
import math
from src.utils import get_config
from datetime import datetime

# --- OpenAI Helper Function ---
def format_openai_messages(context, batch_frames):
    """ Formats messages for OpenAI VLM API. """
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": context},
            ]
        }
    ]
    # Add images - OpenAI expects base64 strings directly in the content list
    for frame_data in batch_frames:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_data}"
            }
        })
    return messages

def calculate_optimal_batch_size(total_frames, max_batch_size=32):
    """
    Calculate an optimal batch size based on the total number of frames.
    
    Args:
        total_frames (int): Total number of frames to process
        max_batch_size (int): Maximum number of frames per batch
        
    Returns:
        int: Optimal batch size
    """
    # For VLMs with large context windows (128k tokens), we can handle more frames
    # Each image might consume ~1000-2000 tokens depending on complexity
    
    if total_frames <= max_batch_size:
        return total_frames  # Process all at once if possible
    
    # Try to use a reasonable batch size that divides the frames evenly
    # Adjusted lower bound for more flexibility
    for batch_size in range(max_batch_size, 8, -1): 
        if total_frames % batch_size == 0 or batch_size >= max_batch_size // 2:
            return batch_size
            
    # If no ideal divisor found, use a reasonably large size
    return min(max_batch_size, total_frames)


def prepare_batches(frames, batch_size=32):
    """
    Prepare frames into batches for processing.
    
    Args:
        frames (list): List of base64-encoded image frames
        batch_size (int, optional): Number of frames to send in each batch. Defaults to 32.
        
    Returns:
        list: List of frame batches
    """
    return [frames[i:i+batch_size] for i in range(0, len(frames), batch_size)]


def process_frames(frames, prompt, batch_size=None, fps=8):
    """
    Process frames with the VLM via the configured endpoint (Ollama or OpenAI).
    
    Args:
        frames (list): List of base64-encoded image frames
        prompt (str): Text prompt for the VLM
        batch_size (int, optional): Number of frames per batch. If None, auto-calculated.
        fps (int, optional): Frames per second the video was sampled at. Defaults to 8.
        
    Returns:
        str: Result from the VLM
    Raises:
        ValueError: If endpoint configuration is invalid.
        ConnectionError: If unable to connect to the service or process frames.
    """
    # Get configuration
    config = get_config()
    endpoint_type = config["endpoint_type"]
    temperature = config["temperature"]
    top_p = config["top_p"]
    print(f"Using Temperature: {temperature}, Top P: {top_p}")
    
    client = None
    model = None
    
    # --- Initialize Client based on Endpoint Type ---
    if endpoint_type == "ollama":
        host = config["ollama_host"]
        model = config["ollama_model"]
        print(f"Creating Ollama client with host: {host}")
        client = ollama.Client(host=host)
        # Verify the client host setting (optional check)
        client_opts = getattr(client, "_client", None)
        if client_opts and hasattr(client_opts, "base_url"):
            print(f"Ollama Client base URL: {client_opts.base_url}")
    elif endpoint_type == "openai":
        api_key = config["openai_api_key"]
        model = config["openai_model"]
        base_url = config.get("openai_base_url") # Use .get for optional value
        print(f"Creating OpenAI client for model: {model}")
        if base_url:
            print(f"Using custom OpenAI base URL: {base_url}")
        # Pass base_url only if it's set
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None,
        )
    else:
        # This case should be caught by get_config validation, but defensively check again
        raise ValueError(f"Invalid ENDPOINT_TYPE configured: {endpoint_type}")

    # Calculate optimal batch size if not provided or if endpoint is OpenAI
    # Note: OpenAI might have different practical limits than Ollama for # images
    if batch_size is None or endpoint_type == 'openai': 
         # Recalculate for OpenAI or if not provided, maybe cap lower for OpenAI?
         # For now, use the same logic, but keep in mind OpenAI's limits might differ.
         # Consider a smaller max_batch_size specifically for OpenAI if needed.
        calculated_batch_size = calculate_optimal_batch_size(len(frames)) 
        if batch_size is not None:
            print(f"Overriding provided batch size {batch_size} with calculated {calculated_batch_size} for OpenAI or auto mode.")
        batch_size = calculated_batch_size
        
    print(f"Using batch size of {batch_size} for {len(frames)} frames with {endpoint_type}")
    
    # --- Route to appropriate processing function ---
    if len(frames) <= batch_size:
        # Process all at once if possible (common case for short videos or large batches)
        return process_all_frames_at_once(client, endpoint_type, model, frames, prompt, fps, temperature, top_p)
    else:
        # Process in batches if needed
        return process_frames_in_batches(client, endpoint_type, model, frames, prompt, batch_size, fps, temperature, top_p)


def process_all_frames_at_once(client, endpoint_type, model, frames, prompt, fps, temperature, top_p):
    """
    Process all frames in a single batch (Ollama or OpenAI).
    
    Args:
        client: Initialized Ollama or OpenAI client
        endpoint_type (str): "ollama" or "openai"
        model (str): Model name
        frames (list): List of base64-encoded image frames
        prompt (str): Text prompt for the VLM
        fps (int): Frames per second
        temperature (float): Temperature for the VLM
        top_p (float): Top P for the VLM
        
    Returns:
        str: Result from the VLM
    """
    print(f"\n--- Processing all {len(frames)} frames in a single batch via {endpoint_type} ---")
    start_time = time.time()
    
    # --- Create Context ---
    context = (
        f"You are analyzing a video sequence of {len(frames)} consecutive frames, sampled at {fps} fps. "
        f"The frames are in chronological order, representing approximately {len(frames)/fps:.2f} seconds of video. "
        f"Since you're seeing all frames together, you have complete temporal context to analyze motion and changes. "
        f"Focus on identifying motion and changes between frames, and analyze how objects/people move and interact over time. "
        f"You are not allowed to ask the user for more information, you are not allowed to hallucinate, you are not allowed to make up information. "
        f"\n\nThe user wants you to: {prompt}"
    )
    
    try:
        # --- Call API based on Endpoint Type ---
        if endpoint_type == "ollama":
            response = client.generate(
                model=model,
                prompt=context,
                images=frames, # Ollama takes list of base64 strings
                stream=False,
                options={
                    'temperature': temperature,
                    'top_p': top_p
                }
            )
            result = response.get("response", "")
        elif endpoint_type == "openai":
            messages = format_openai_messages(context, frames)
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p
            )
            result = response.choices[0].message.content if response.choices else ""
        else:
            raise ValueError(f"Unsupported endpoint type for single batch: {endpoint_type}")

        end_time = time.time()
        duration = end_time - start_time
        
        if not result:
             raise ValueError(f"API call to {endpoint_type} returned an empty response.")

        # --- Format Result with Stats ---
        result_with_stats = (
            f"{result}\n\n"
            f"--- Performance Statistics ---\n"
            f"Total runtime: {duration:.2f} seconds\n"
            f"Frames processed: {len(frames)} in a single batch via {endpoint_type}\n"
            # f"Time per frame: {duration/len(frames):.2f} seconds\n" # Less meaningful for batch
            f"Processing approach: Single batch (perfect temporal alignment)\n"
            f"Context window utilization: Full sequence analysis"
        )
            
        return result_with_stats
            
    except Exception as e:
        # More specific error logging
        error_type = type(e).__name__
        print(f"Error during {endpoint_type} API call (single batch): {error_type} - {e}")
        raise ConnectionError(f"Failed to process frames via {endpoint_type}: {e}")


# Renamed from process_frames_with_temporal_awareness for clarity
def process_frames_in_batches(client, endpoint_type, model, frames, prompt, batch_size, fps, temperature, top_p): 
    """
    Process frames in multiple batches (Ollama or OpenAI) with temporal awareness.
    
    Args:
        client: Initialized Ollama or OpenAI client
        endpoint_type (str): "ollama" or "openai"
        model (str): Model name
        frames (list): List of base64-encoded image frames
        prompt (str): Text prompt for the VLM
        batch_size (int): Number of frames per batch
        fps (int): Frames per second
        temperature (float): Temperature for the VLM
        top_p (float): Top P for the VLM
        
    Returns:
        str: Result from the VLM
    """
    overall_start_time = time.time()
    batches = prepare_batches(frames, batch_size)
    print(f"Created {len(batches)} batches with up to {batch_size} frames each for {endpoint_type}")
    
    responses = []
    batch_times = []
    previous_observations = "" # Keep track for context carry-over (optional but good)
    
    for i, batch in enumerate(batches):
        batch_start_time_perf = time.time() # For performance timing only
        try:
            batch_start_frame = i * batch_size
            # Adjust end frame calculation for 0-based indexing and list length
            batch_end_frame = batch_start_frame + len(batch) - 1 
            
            start_time_sec = batch_start_frame / fps
            end_time_sec = (batch_end_frame) / fps # Use the actual last frame index

            print(f"\n--- Processing batch {i+1} of {len(batches)} via {endpoint_type} ---")
            # Use 1-based frame numbers for user-facing print, but keep 0-based for calculations
            print(f"Frames {batch_start_frame + 1}-{batch_end_frame + 1} (time: {start_time_sec:.2f}s-{end_time_sec:.2f}s)")
            
            # --- Create Context for the current batch ---
            context = (
                f"You are analyzing a sequence of {len(batch)} consecutive frames ({batch_start_frame + 1} to {batch_end_frame + 1}) "
                f"from a video sampled at {fps} fps, representing video timestamps {start_time_sec:.2f}s to {end_time_sec:.2f}s. "
                f"Focus on identifying motion and temporal changes *within this specific segment*. "
                f"Use bounding boxes or other visual features to identify the location of the characters in the video sequence to help with the analysis. "
                f"DO NOT GUESS OR HALLUCINATE. SIMPLY REPORT WHAT YOU SEE. ONLY REPORT WHAT YOU SEE IN THE FRAMES."
            )
            
            # --- Add context from previous batch (optional but helpful) ---
            # Note: This increases token count, be mindful of limits, especially for OpenAI
            if previous_observations and i > 0:
                 # Calculate previous segment time for clarity
                 prev_start_frame = (i-1) * batch_size
                 prev_end_frame = prev_start_frame + batch_size - 1 # Assuming full previous batch
                 prev_start_sec = prev_start_frame / fps
                 prev_end_sec = prev_end_frame / fps
                 context += (f"\n\nObservations from the immediately preceding segment "
                             f"(Time {prev_start_sec:.2f}s-{prev_end_sec:.2f}s): {previous_observations}\n\n")

            # Add the main user prompt
            context += f"The user wants you to analyze this current segment ({start_time_sec:.2f}s-{end_time_sec:.2f}s) based on this prompt: {prompt}"

            # --- Call API based on Endpoint Type ---
            batch_response_text = ""
            if endpoint_type == "ollama":
                response = client.generate(
                    model=model,
                    prompt=context,
                    images=batch,
                    stream=False,
                    options={
                        'temperature': temperature,
                        'top_p': top_p
                    }
                )
                batch_response_text = response.get("response", "")
            elif endpoint_type == "openai":
                messages = format_openai_messages(context, batch)
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p
                )
                batch_response_text = response.choices[0].message.content if response.choices else ""
            else:
                 raise ValueError(f"Unsupported endpoint type for batch processing: {endpoint_type}")

            if not batch_response_text:
                 print(f"Warning: API call to {endpoint_type} for batch {i+1} returned an empty response.")
                 # Decide how to handle: skip, use placeholder, or raise error? For now, use placeholder.
                 batch_response_text = "(No response from API for this segment)"

            responses.append(batch_response_text)
            previous_observations = batch_response_text # Update for next iteration

            batch_end_time_perf = time.time()
            batch_duration = batch_end_time_perf - batch_start_time_perf
            batch_times.append(batch_duration)

            print(f"\nBatch {i+1} Response (processed in {batch_duration:.2f} seconds):")
            print("-" * 40)
            print(batch_response_text)
            print("-" * 40)
            
            # Add a small delay between API calls to avoid rate limits
            if i < len(batches) - 1:
                time.sleep(1) # Keep delay for both
                
        except Exception as e:
            error_type = type(e).__name__
            print(f"Error during {endpoint_type} API call (batch {i+1}): {error_type} - {e}")
            # Option: Allow continuing to next batch? Or raise immediately? Raising is safer.
            raise ConnectionError(f"Failed to process batch {i+1} via {endpoint_type}: {e}")
    
    # --- Generate Final Summary ---
    try:
        print(f"\n--- Generating final temporally-aware summary via {endpoint_type} ---")
        summary_start_time = time.time()

        segment_summaries = chr(10).join([
             # Use calculated time for final summary prompt
             f"Segment {i+1} (Time {i*batch_size/fps:.2f}s - {(i*batch_size + len(batch) -1)/fps:.2f}s): {resp}" 
            for i, (batch, resp) in enumerate(zip(batches, responses)) # Need batch length here
        ])

        final_instruction = f"""Based *only* on the detailed observations provided above for each time segment, generate a final, comprehensive response to the user's prompt: '{prompt}'.

Please structure your response as follows:
1.  **Chronological Timeline:** Create a clear, structured timeline of events using the provided timestamps (e.g., "Time 0.0s - 3.1s:", "Time 3.2s - 6.3s:", etc.). Describe the key actions, movements, and changes occurring within each time segment based *only* on the segment summaries. Do NOT refer back to frame numbers.
2.  **Key Event Highlights (Optional but encouraged):** If possible, identify and list 1-3 most significant events or transitions observed in the video, along with their approximate start times (e.g., "- X begins (~3.6s)").
3.  **Overall Summary:** Briefly summarize the main narrative or activity depicted across the entire analyzed duration, synthesizing the timeline information.
4. Character names may be supplied in the prompt, if so, use them in the response IF they exist and are seen in the video sequence ONLY.

Focus on accurately reflecting the information from the segment summaries using the time references. Ensure the timeline flows logically based on the sequential observations. Adhere strictly to the observations provided in the segments above. This is NOT interactive, you are not allowed to ask the user for more information.
"""

        final_context = f"""I have analyzed {len(frames)} sequential frames from a video sampled at {fps} fps, representing approximately {len(frames)/fps:.2f} seconds of video content via {endpoint_type}.

Here are my detailed observations from analyzing the video in {len(batches)} segments:

{segment_summaries}

{final_instruction}
"""
        # --- Call Final Summary API ---
        final_result = ""
        if endpoint_type == "ollama":
             # Ollama final summary doesn't need images
             final_response = client.generate(
                 model=model,
                 prompt=final_context,
                 stream=False,
                 options={
                     'temperature': temperature,
                     'top_p': top_p
                 }
             )
             final_result = final_response.get("response", "")
        elif endpoint_type == "openai":
             # OpenAI final summary also doesn't need images
             messages = [{"role": "user", "content": final_context}]
             final_response = client.chat.completions.create(
                 model=model,
                 messages=messages,
                 temperature=temperature,
                 top_p=top_p
             )
             final_result = final_response.choices[0].message.content if final_response.choices else ""
        else:
             raise ValueError(f"Unsupported endpoint type for final summary: {endpoint_type}")


        if not final_result:
            raise ValueError(f"Final summary API call to {endpoint_type} returned an empty response.")

        summary_end_time = time.time()
        summary_duration = summary_end_time - summary_start_time
        overall_end_time = time.time()
        overall_duration = overall_end_time - overall_start_time

        # --- Format Final Result with Stats ---
        final_result_with_stats = (
            f"{final_result}\n\n"
            f"--- Performance Statistics ---\n"
            f"Total runtime: {overall_duration:.2f} seconds\n"
            f"Frames processed: {len(frames)} in {len(batches)} batches of up to {batch_size} frames each via {endpoint_type}\n"
            f"Processing approach: Batched processing with temporal context\n"
            f"Average time per batch: {sum(batch_times) / len(batch_times) if batch_times else 0:.2f} seconds\n"
            f"Summary generation time: {summary_duration:.2f} seconds"
        )
            
        return final_result_with_stats
            
    except Exception as e:
        error_type = type(e).__name__
        print(f"Error during {endpoint_type} final summary generation: {error_type} - {e}")
        raise ConnectionError(f"Failed to generate final summary via {endpoint_type}: {e}")
