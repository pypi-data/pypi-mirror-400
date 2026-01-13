"""
Audio detection module for AI-generated audio content.

Provides multiple detectors for identifying synthetic audio:
- SpectralSignal: Frequency domain analysis (lightweight)
- Wav2VecSignal: Foundation model approach (high accuracy)
- AASISTSignal: Spectro-temporal analysis
- BreathingSignal: Breath pattern analysis (heuristic)
"""

from veridex.audio.spectral import SpectralSignal
from veridex.audio.wav2vec_signal import Wav2VecSignal
from veridex.audio.aasist_signal import AASISTSignal
from veridex.audio.breathing_signal import BreathingSignal
from veridex.audio.silence import SilenceSignal

__all__ = [
    "SpectralSignal",
    "Wav2VecSignal",
    "AASISTSignal",
    "BreathingSignal",
    "SilenceSignal",
]
