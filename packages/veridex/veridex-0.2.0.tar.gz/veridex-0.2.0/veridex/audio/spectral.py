"""
Spectral analysis detector for audio deepfakes.

Detects artifacts from neural vocoders by analyzing frequency domain anomalies,
particularly in high-frequency regions (>8kHz) where phase discontinuities
and spectral envelope irregularities are common in synthetic audio.
"""

from typing import Any, Union
from pathlib import Path
import numpy as np
from veridex.core.signal import BaseSignal, DetectionResult


class SpectralSignal(BaseSignal):
    """
    Detects AI-generated audio by analyzing spectral anomalies.
    
    This detector focuses on artifacts left by neural vocoders (like HiFi-GAN, WaveGlow),
    which often exhibit:
    - High-frequency phase discontinuities (>8kHz)
    - Unnatural spectral envelope patterns
    - Anomalous energy distribution across frequency bands
    
    This is a lightweight, CPU-friendly detector suitable for real-time use.

    Attributes:
        name (str): 'spectral_audio_detector'
        dtype (str): 'audio'
    """
    
    def __init__(
        self,
        target_sr: int = 16000,
        n_fft: int = 2048,
        hop_length: int = 512,
    ):
        """
        Initialize the spectral detector.
        
        Args:
            target_sr: Target sample rate for audio resampling
            n_fft: FFT window size
            hop_length: Hop length for STFT
        """
        self.target_sr = target_sr
        self.n_fft = n_fft
        self.hop_length = hop_length
    
    @property
    def name(self) -> str:
        return "spectral_audio_detector"
    
    @property
    def dtype(self) -> str:
        return "audio"
    
    def check_dependencies(self) -> None:
        try:
            import librosa
            import soundfile
            import scipy
        except ImportError:
            raise ImportError(
                "Audio detection requires 'librosa', 'soundfile', and 'scipy'. "
                "Install with: pip install veridex[audio]"
            )
    
    def run(self, input_data: Any) -> DetectionResult:
        """
        Analyze audio for AI-generation artifacts.
        
        Args:
            input_data: Path to audio file (str or Path)
            
        Returns:
            DetectionResult with score, confidence, and spectral metadata
        """
        if not isinstance(input_data, (str, Path)):
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error="Input must be a file path (str or Path)"
            )
        
        try:
            self.check_dependencies()
        except ImportError as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error=str(e)
            )
        
        try:
            from veridex.audio.utils import load_audio, validate_audio, compute_spectrogram
            import scipy.signal as signal
            import scipy.stats as stats
            
            # Load audio
            audio, sr = load_audio(input_data, target_sr=self.target_sr)
            
            # Validate audio
            is_valid, error_msg = validate_audio(audio, sr)
            if not is_valid:
                return DetectionResult(
                    score=0.0,
                    confidence=0.0,
                    error=error_msg
                )
            
            # Compute spectrogram
            spectrogram = compute_spectrogram(
                audio,
                sr=sr,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            
            # Analyze spectral features
            features = self._extract_spectral_features(spectrogram, sr)
            
            # Compute AI probability score
            score = self._compute_score(features)
            
            # Estimate confidence based on audio quality
            confidence = self._estimate_confidence(audio, features)
            
            return DetectionResult(
                score=score,
                confidence=confidence,
                metadata=features
            )
            
        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error=f"Spectral analysis failed: {e}"
            )
    
    def _extract_spectral_features(
        self,
        spectrogram: np.ndarray,
        sr: int
    ) -> dict:
        """Extract features for deepfake detection."""
        import scipy.stats as stats
        
        # Frequency bins
        freqs = np.fft.rfftfreq(self.n_fft, 1/sr)
        
        # Separate low/mid/high frequency regions
        low_freq_mask = freqs < 2000  # < 2kHz
        mid_freq_mask = (freqs >= 2000) & (freqs < 8000)  # 2-8 kHz
        high_freq_mask = freqs >= 8000  # > 8kHz (vocoder artifacts region)
        
        # Energy in each band (average over time)
        low_energy = np.mean(spectrogram[low_freq_mask, :])
        mid_energy = np.mean(spectrogram[mid_freq_mask, :])
        high_energy = np.mean(spectrogram[high_freq_mask, :])
        
        # Spectral roll-off (frequency below which 85% of energy concentrates)
        spectral_rolloff = self._compute_rolloff(spectrogram, freqs)
        
        # High-frequency entropy (natural audio has chaotic high-freq)
        high_freq_entropy = stats.entropy(
            spectrogram[high_freq_mask, :].flatten() + 1e-10
        )
        
        # Spectral flatness (measure of "noisiness")
        spectral_flatness = self._compute_flatness(spectrogram)
        
        # Temporal stability in high frequencies
        # AI vocoders often produce overly stable high-freq patterns
        high_freq_stability = np.std(
            np.mean(spectrogram[high_freq_mask, :], axis=0)
        )
        
        return {
            "low_freq_energy": float(low_energy),
            "mid_freq_energy": float(mid_energy),
            "high_freq_energy": float(high_energy),
            "spectral_rolloff": float(spectral_rolloff),
            "high_freq_entropy": float(high_freq_entropy),
            "spectral_flatness": float(spectral_flatness),
            "high_freq_stability": float(high_freq_stability),
        }
    
    def _compute_rolloff(self, spectrogram: np.ndarray, freqs: np.ndarray) -> float:
        """Compute spectral roll-off point."""
        # Average over time
        avg_spectrum = np.mean(spectrogram, axis=1)
        
        # Cumulative energy
        cumsum = np.cumsum(avg_spectrum)
        total = cumsum[-1]
        
        # Find frequency where 85% of energy is below
        threshold = 0.85 * total
        rolloff_idx = np.where(cumsum >= threshold)[0]
        
        if len(rolloff_idx) > 0:
            return freqs[rolloff_idx[0]]
        return freqs[-1]
    
    def _compute_flatness(self, spectrogram: np.ndarray) -> float:
        """Compute spectral flatness (geometric mean / arithmetic mean)."""
        # Average over time
        avg_spectrum = np.mean(spectrogram, axis=1) + 1e-10
        
        # Geometric mean
        geo_mean = np.exp(np.mean(np.log(avg_spectrum)))
        
        # Arithmetic mean
        arith_mean = np.mean(avg_spectrum)
        
        flatness = geo_mean / arith_mean
        return float(flatness)
    
    def _compute_score(self, features: dict) -> float:
        """
        Compute AI probability score from spectral features.
        
        Heuristic scoring based on typical vocoder artifacts:
        - AI audio tends to have lower high-frequency energy
        - Lower spectral roll-off (energy concentrated in lower frequencies)
        - Lower high-frequency entropy (more regular patterns)
        - Higher temporal stability in high frequencies
        """
        score = 0.0
        
        # 1. High-frequency energy (AI typically has less)
        # Natural speech: high_energy > 10, AI: < 5
        if features["high_freq_energy"] < 5.0:
            score += 0.3
        elif features["high_freq_energy"] < 10.0:
            score += 0.15
        
        # 2. Spectral rolloff (AI concentrates energy lower)
        # Natural: > 6000 Hz, AI: < 4000 Hz
        if features["spectral_rolloff"] < 4000:
            score += 0.25
        elif features["spectral_rolloff"] < 6000:
            score += 0.1
        
        # 3. High-frequency entropy (AI is more regular)
        # Natural: > 5.0, AI: < 3.0
        if features["high_freq_entropy"] < 3.0:
            score += 0.25
        elif features["high_freq_entropy"] < 5.0:
            score += 0.1
        
        # 4. High-frequency stability (AI is more stable)
        # Natural: > 2.0, AI: < 1.0
        if features["high_freq_stability"] < 1.0:
            score += 0.2
        elif features["high_freq_stability"] < 2.0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_confidence(self, audio: np.ndarray, features: dict) -> float:
        """
        Estimate confidence based on audio quality and feature reliability.
        """
        confidence = 0.7  # Base confidence
        
        # Reduce confidence for very short audio
        duration = len(audio) / self.target_sr
        if duration < 2.0:
            confidence *= 0.6
        elif duration < 5.0:
            confidence *= 0.8
        
        # Reduce confidence if features are borderline
        if 4000 <= features["spectral_rolloff"] <= 6000:
            confidence *= 0.9
        
        return min(confidence, 1.0)
