"""Lightweight video processing utilities."""
import numpy as np
from typing import List, Tuple, Iterator, Literal

def chunk_video_frames(
    frames: np.ndarray, 
    chunk_size: int, 
    overlap: int = 0
) -> Iterator[Tuple[int, np.ndarray]]:
    """
    Yield chunks of video frames for processing long videos.
    
    Args:
        frames: (T, H, W, C) array
        chunk_size: Frames per chunk
        overlap: Overlapping frames between chunks
        
    Yields:
        (start_idx, chunk_frames)
        
    Example:
        >>> frames = np.zeros((1000, 224, 224, 3))
        >>> for start, chunk in chunk_video_frames(frames, 300, overlap=30):
        ...     # Process chunk of 300 frames
        ...     result = process(chunk)
    """
    total_frames = len(frames)
    stride = chunk_size - overlap
    
    for start in range(0, total_frames, stride):
        end = min(start + chunk_size, total_frames)
        yield start, frames[start:end]
        
        if end >= total_frames:
            break

def smart_sample_frames(
    total_frames: int, 
    target_frames: int, 
    strategy: Literal['uniform', 'random'] = 'uniform'
) -> List[int]:
    """
    Sample frame indices intelligently.
    
    Args:
        total_frames: Total available frames
        target_frames: Desired number of frames
        strategy: 'uniform' (evenly spaced) or 'random'
        
    Returns:
        List of frame indices to sample
        
    Example:
        >>> indices = smart_sample_frames(300, 64, 'uniform')
        >>> len(indices)
        64
    """
    if target_frames >= total_frames:
        return list(range(total_frames))
    
    if strategy == 'uniform':
        return np.linspace(0, total_frames - 1, target_frames, dtype=int).tolist()
    elif strategy == 'random':
        return sorted(np.random.choice(total_frames, target_frames, replace=False))
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Use 'uniform' or 'random'")

def validate_video_file(file_path: str) -> Tuple[bool, str, dict]:
    """
    Validate video file and extract metadata.
    
    Args:
        file_path: Path to video file
        
    Returns:
        (is_valid, error_message, metadata_dict)
        
    Example:
        >>> valid, error, meta = validate_video_file('video.mp4')
        >>> if valid:
        ...     print(f"FPS: {meta['fps']}, Frames: {meta['total_frames']}")
    """
    import os
    import cv2
    
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}", {}
    
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        return False, "Unable to open video file. Format may be unsupported.", {}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    metadata = {
        'fps': fps,
        'total_frames': total_frames,
        'width': width,
        'height': height,
        'duration_seconds': total_frames / fps if fps > 0 else 0
    }
    
    if total_frames < 30:
        return False, "Video too short (< 1 second)", metadata
    
    return True, "", metadata
