"""
Audio detection utilities for loading, preprocessing, and feature extraction.
"""

from typing import Tuple, Optional, Union
import numpy as np
from pathlib import Path


def load_audio(
    file_path: Union[str, Path],
    target_sr: int = 16000,
    mono: bool = True,
    duration: Optional[float] = None,
) -> Tuple[np.ndarray, int]:
    """
    Load an audio file and preprocess it.
    
    Args:
        file_path: Path to the audio file
        target_sr: Target sample rate (Hz)
        mono: Convert to mono if True
        duration: Maximum duration in seconds (None for full file)
        
    Returns:
        Tuple of (audio_data, sample_rate)
        
    Raises:
        ImportError: If librosa/soundfile not installed
        ValueError: If file cannot be loaded
    """
    try:
        import librosa
        import soundfile as sf
    except ImportError:
        raise ImportError(
            "Audio processing requires 'librosa' and 'soundfile'. "
            "Install with: pip install veridex[audio]"
        )
    
    try:
        # Load audio file
        audio, sr = librosa.load(
            file_path,
            sr=target_sr,
            mono=mono,
            duration=duration
        )
        
        # Normalize audio to [-1, 1]
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val
            
        return audio, sr
        
    except Exception as e:
        raise ValueError(f"Failed to load audio file '{file_path}': {e}")


def extract_mel_spectrogram(
    audio: np.ndarray,
    sr: int = 16000,
    n_mels: int = 128,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> np.ndarray:
    """
    Extract mel-spectrogram from audio signal.
    
    Args:
        audio: Audio signal
        sr: Sample rate
        n_mels: Number of mel bands
        n_fft: FFT window size
        hop_length: Hop length for STFT
        
    Returns:
        Mel-spectrogram (n_mels x time)
    """
    try:
        import librosa
    except ImportError:
        raise ImportError(
            "Librosa is required for mel-spectrogram extraction. "
            "Install with: pip install veridex[audio]"
        )
    
    # Compute mel-spectrogram
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=n_mels,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    # Convert to log scale (dB)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    return mel_spec_db


def extract_mfcc(
    audio: np.ndarray,
    sr: int = 16000,
    n_mfcc: int = 40,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> np.ndarray:
    """
    Extract MFCC features from audio signal.
    
    Args:
        audio: Audio signal
        sr: Sample rate
        n_mfcc: Number of MFCCs to extract
        n_fft: FFT window size
        hop_length: Hop length for STFT
        
    Returns:
        MFCC matrix (n_mfcc x time)
    """
    try:
        import librosa
    except ImportError:
        raise ImportError(
            "Librosa is required for MFCC extraction. "
            "Install with: pip install veridex[audio]"
        )
    
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    return mfcc


def compute_spectrogram(
    audio: np.ndarray,
    sr: int = 16000,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> np.ndarray:
    """
    Compute magnitude spectrogram.
    
    Args:
        audio: Audio signal
        sr: Sample rate
        n_fft: FFT window size
        hop_length: Hop length
        
    Returns:
        Magnitude spectrogram
    """
    try:
        import librosa
    except ImportError:
        raise ImportError(
            "Librosa is required for spectrogram computation. "
            "Install with: pip install veridex[audio]"
        )
    
    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft)
    
    return magnitude


def validate_audio(
    audio: np.ndarray,
    sr: int,
    min_duration: float = 0.5,
    max_duration: float = 60.0,
) -> Tuple[bool, Optional[str]]:
    """
    Validate audio data meets basic requirements.
    
    Args:
        audio: Audio signal
        sr: Sample rate
        min_duration: Minimum required duration (seconds)
        max_duration: Maximum allowed duration (seconds)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    duration = len(audio) / sr
    
    if duration < min_duration:
        return False, f"Audio too short: {duration:.2f}s < {min_duration}s"
    
    if duration > max_duration:
        return False, f"Audio too long: {duration:.2f}s > {max_duration}s"
    
    if np.all(audio == 0):
        return False, "Audio signal is silent"
    
    if np.any(~np.isfinite(audio)):
        return False, "Audio contains invalid values (NaN or Inf)"
    
    return True, None
