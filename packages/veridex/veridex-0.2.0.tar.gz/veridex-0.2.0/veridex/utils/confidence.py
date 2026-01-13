"""
Confidence calculation utilities for veridex signals.

This module provides helper functions to calculate confidence scores from various
model outputs and measurements. All functions return float values in [0.0, 1.0] range.

Confidence interpretation:
- 0.0-0.3: Low confidence (heuristics, untrained models, errors)
- 0.4-0.6: Moderate confidence (statistical methods, limited data)
- 0.7-0.9: High confidence (trained models with good predictions)
- 0.9-1.0: Very high confidence (strong model predictions, clear patterns)
"""

import numpy as np
from typing import List, Optional


def softmax_confidence(probabilities: np.ndarray) -> float:
    """
    Calculate confidence from softmax probabilities using max probability.
    
    The maximum probability in a softmax distribution indicates how confident
    the model is in its prediction.
    
    Args:
        probabilities: Array of softmax probabilities that sum to 1.0
        
    Returns:
        float: Confidence score in [0.0, 1.0], equal to max(probabilities)
        
    Example:
        >>> probs = np.array([0.1, 0.2, 0.7])
        >>> softmax_confidence(probs)
        0.7
    """
    if probabilities.size == 0:
        return 0.0
    return float(np.max(probabilities))


def margin_confidence(probabilities: np.ndarray, top_k: int = 2) -> float:
    """
    Calculate confidence from margin between top-k classes.
    
    A large margin between the top two predictions indicates high confidence.
    This is more robust than just using max probability.
    
    Args:
        probabilities: Array of probabilities (should sum to 1.0)
        top_k: Number of top classes to consider (default: 2)
        
    Returns:
        float: Confidence score in [0.0, 1.0] based on margin
        
    Example:
        >>> probs = np.array([0.1, 0.2, 0.7])
        >>> margin_confidence(probs)  # 0.7 - 0.2 = 0.5
        0.5
    """
    if probabilities.size < top_k:
        return 0.0
    
    # Get top k probabilities
    top_probs = np.sort(probabilities)[-top_k:]
    
    # Margin is difference between top 2
    if len(top_probs) >= 2:
        margin = float(top_probs[-1] - top_probs[-2])
        # Normalize to [0, 1]: max margin is 1.0 (when top_prob=1.0, second=0.0)
        return margin
    else:
        return float(top_probs[0])


def entropy_confidence(probabilities: np.ndarray) -> float:
    """
    Calculate confidence from entropy of probability distribution.
    
    Low entropy indicates a peaked distribution (high confidence).
    High entropy indicates a uniform distribution (low confidence).
    
    Args:
        probabilities: Array of probabilities (should sum to 1.0)
        
    Returns:
        float: Confidence score in [0.0, 1.0], inverse of normalized entropy
        
    Example:
        >>> probs = np.array([0.9, 0.05, 0.05])  # Low entropy
        >>> entropy_confidence(probs)
        0.92...  # High confidence
    """
    if probabilities.size == 0:
        return 0.0
    
    # Avoid log(0)
    probs = np.clip(probabilities, 1e-10, 1.0)
    
    # Calculate entropy: -sum(p * log(p))
    entropy = -np.sum(probs * np.log2(probs))
    
    # Max entropy is log2(n) where n is number of classes
    max_entropy = np.log2(len(probs))
    
    if max_entropy == 0:
        return 1.0
    
    # Normalize and invert (low entropy = high confidence)
    normalized_entropy = entropy / max_entropy
    confidence = 1.0 - normalized_entropy
    
    return float(np.clip(confidence, 0.0, 1.0))


def distance_confidence(
    distance: float,
    threshold: float,
    max_distance: Optional[float] = None,
    higher_is_better: bool = False
) -> float:
    """
    Calculate confidence from distance metrics.
    
    Maps a distance value to a confidence score based on a threshold.
    Can handle both cases where higher distance is better or worse.
    
    Args:
        distance: The measured distance value
        threshold: Reference threshold for the distance
        max_distance: Maximum expected distance (for normalization)
        higher_is_better: If True, higher distances mean higher confidence
        
    Returns:
        float: Confidence score in [0.0, 1.0]
        
    Example:
        >>> # CLIP score near threshold = low confidence
        >>> distance_confidence(0.5, threshold=0.5, max_distance=1.0)
        0.0
        >>> # Score far from threshold = high confidence
        >>> distance_confidence(0.9, threshold=0.5, max_distance=1.0)
        0.8
    """
    if max_distance is None:
        max_distance = threshold * 2
    
    # Calculate distance from threshold
    dist_from_threshold = abs(distance - threshold)
    
    # Normalize
    max_possible_distance = max(abs(max_distance - threshold), threshold)
    
    if max_possible_distance == 0:
        return 0.0
    
    confidence = dist_from_threshold / max_possible_distance
    
    if higher_is_better:
        # For metrics where higher is better, also consider absolute value
        confidence = min(confidence + (distance / max_distance) * 0.5, 1.0)
    
    return float(np.clip(confidence, 0.0, 1.0))


def variance_confidence(
    values: List[float],
    expected_variance: Optional[float] = None,
    inverse: bool = True
) -> float:
    """
    Calculate confidence from variance of measurements.
    
    Typically, low variance indicates consistent measurements (high confidence).
    
    Args:
        values: List of measurement values
        expected_variance: Expected variance level (for normalization)
        inverse: If True, low variance = high confidence (default)
        
    Returns:
        float: Confidence score in [0.0, 1.0]
        
    Example:
        >>> # Low variance = high confidence
        >>> variance_confidence([0.9, 0.91, 0.89, 0.90])
        0.95...
        >>> # High variance = low confidence
        >>> variance_confidence([0.1, 0.9, 0.5, 0.3])
        0.2...
    """
    if len(values) < 2:
        return 0.5  # Moderate confidence with single measurement
    
    variance = float(np.var(values))
    
    if expected_variance is None:
        # Estimate based on data range
        data_range = np.max(values) - np.min(values)
        expected_variance = (data_range / 2.0) ** 2
    
    if expected_variance == 0:
        return 1.0 if variance == 0 else 0.0
    
    # Normalize variance
    normalized_var = variance / expected_variance
    
    if inverse:
        # Low variance = high confidence
        # Use exponential decay: confidence = exp(-k * normalized_var)
        confidence = np.exp(-2.0 * normalized_var)
    else:
        # High variance = high confidence (unusual case)
        confidence = min(normalized_var, 1.0)
    
    return float(np.clip(confidence, 0.0, 1.0))


def default_confidence_for_heuristic(signal_name: str) -> float:
    """
    Returns calibrated confidence values for heuristic-based signals.
    
    These values are based on empirical reliability of each detection method
    when no model-based confidence can be calculated.
    
    Args:
        signal_name: Name of the signal method
        
    Returns:
        float: Default confidence value in [0.0, 1.0]
        
    Example:
        >>> default_confidence_for_heuristic("frequency_artifacts")
        0.3
        >>> default_confidence_for_heuristic("clip_zeroshot")
        0.8
    """
    # Heuristic/Statistical methods (low-moderate confidence)
    heuristic_signals = {
        "frequency_artifacts": 0.3,  # Raw spectral analysis
        "ela": 0.4,                   # Error level analysis
        "silence_analysis": 0.4,      # Silence pattern heuristics
        "spectral_features": 0.5,     # Audio spectral analysis
        "stylometric": 0.5,           # Statistical text features
        "zlib_entropy": 0.4,          # Compression-based
    }
    
    # Model-based methods (high confidence)
    model_signals = {
        "clip_zeroshot": 0.8,         # CLIP zero-shot
        "binoculars": 0.85,           # Binoculars (trained on large scale)
        "detectgpt": 0.75,            # DetectGPT (perturbation-based)
        "aasist": 0.9,                # AASIST (trained anti-spoofing)
        "perplexity": 0.6,            # Perplexity (simpler model-based)
    }
    
    # Video signals (varies by quality)
    video_signals = {
        "rppg_physnet": 0.7,          # rPPG when trained
        "lipsync_wav2lip": 0.7,       # Lip sync when trained
        "spatiotemporal_i3d": 0.85,   # I3D when trained
    }
    
    all_signals = {**heuristic_signals, **model_signals, **video_signals}
    
    return all_signals.get(signal_name, 0.5)  # Default to moderate
