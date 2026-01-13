"""
AASIST-inspired detector for audio anti-spoofing.

Implements spectro-temporal feature extraction based on the AASIST
architecture (Audio Anti-Spoofing using Integrated Spectro-Temporal
Graph Attention Networks). Uses spectral and temporal features to
detect deepfakes.

Note: Full AASIST requires complex graph attention networks. This
implementation provides a feature-based approach that captures the
key insights without requiring the full architecture.
"""

from typing import Any, Union
from pathlib import Path
import numpy as np
from veridex.core.signal import BaseSignal, DetectionResult


class AASISTSignal(BaseSignal):
    """
    AASIST-inspired audio deepfake detector.
    
    Extracts spectro-temporal features that are effective for detecting vocoder artifacts:
    - Temporal variation patterns in spectral components
    - Non-local correlations between frequency and time
    - Phase coherence across frequency bands
    
    This implementation provides a feature-based approach that captures the key insights
    of the AASIST architecture without the full graph attention network complexity,
    balancing accuracy and computational efficiency.

    Attributes:
        name (str): 'aasist_audio_detector'
        dtype (str): 'audio'
    """
    
    def __init__(
        self,
        target_sr: int = 16000,
        n_fft: int = 512,
        hop_length: int = 256,
    ):
        """
        Initialize the AASIST-inspired detector.
        
        Args:
            target_sr: Target sample rate
            n_fft: FFT window size
            hop_length: Hop length for STFT
        """
        self.target_sr = target_sr
        self.n_fft = n_fft
        self.hop_length = hop_length
    
    @property
    def name(self) -> str:
        return "aasist_audio_detector"
    
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
                "AASIST detector requires 'librosa', 'soundfile', and 'scipy'. "
                "Install with: pip install veridex[audio]"
            )
    
    def run(self, input_data: Any) -> DetectionResult:
        """
        Analyze audio using spectro-temporal features.
        
        Args:
            input_data: Path to audio file (str or Path)
            
        Returns:
            DetectionResult with score, confidence, and feature metadata
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
            from veridex.audio.utils import (
                load_audio,
                validate_audio,
                extract_mel_spectrogram,
            )
            import scipy.stats as stats
            
            # Load audio
            audio, sr = load_audio(input_data, target_sr=self.target_sr)
            
            # Validate
            is_valid, error_msg = validate_audio(audio, sr)
            if not is_valid:
                return DetectionResult(
                    score=0.0,
                    confidence=0.0,
                    error=error_msg
                )
            
            # Extract mel-spectrogram
            mel_spec = extract_mel_spectrogram(
                audio,
                sr=sr,
                n_mels=80,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            
            # Extract spectro-temporal features
            features = self._extract_spectro_temporal_features(mel_spec, audio, sr)
            
            # Compute AI probability score
            score = self._compute_score(features)
            
            # Estimate confidence
            confidence = self._estimate_confidence(audio, features, sr)
            
            return DetectionResult(
                score=score,
                confidence=confidence,
                metadata=features
            )
            
        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error=f"AASIST analysis failed: {e}"
            )
    
    def _extract_spectro_temporal_features(
        self,
        mel_spec: np.ndarray,
        audio: np.ndarray,
        sr: int
    ) -> dict:
        """
        Extract spectro-temporal features inspired by AASIST.
        """
        import scipy.stats as stats
        from scipy.signal import stft
        
        # 1. Temporal modulation features
        # Measure variation in each frequency band over time
        temporal_variation = np.std(mel_spec, axis=1)
        mean_temporal_variation = float(np.mean(temporal_variation))
        max_temporal_variation = float(np.max(temporal_variation))
        
        # 2. Spectral modulation features
        # Measure variation across frequency at each time
        spectral_variation = np.std(mel_spec, axis=0)
        mean_spectral_variation = float(np.mean(spectral_variation))
        
        # 3. Phase coherence
        # AI vocoders often have unnatural phase relationships
        f, t, Zxx = stft(audio, fs=sr, nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        phase = np.angle(Zxx)
        
        # Phase derivative (instantaneous frequency deviation)
        phase_diff = np.diff(phase, axis=1)
        phase_coherence = float(np.mean(np.abs(phase_diff)))
        phase_std = float(np.std(phase_diff))
        
        # 4. Energy distribution over time
        # AI often has more uniform energy distribution
        frame_energy = np.sum(mel_spec, axis=0)
        energy_entropy = float(stats.entropy(frame_energy + 1e-10))
        energy_uniformity = float(1.0 / (1.0 + np.std(frame_energy)))
        
        # 5. Cross-correlation between frequency bands
        # Natural speech has specific correlations, AI differs
        # Sample a few bands to reduce computation
        bands = [0, mel_spec.shape[0]//4, mel_spec.shape[0]//2, 3*mel_spec.shape[0]//4, -1]
        correlations = []
        for i in range(len(bands) - 1):
            band1 = mel_spec[bands[i], :]
            band2 = mel_spec[bands[i+1], :]
            corr = np.corrcoef(band1, band2)[0, 1]
            if not np.isnan(corr):
                correlations.append(abs(corr))
        
        mean_band_correlation = float(np.mean(correlations)) if correlations else 0.0
        
        # 6. Spectral flux (measure of spectral change)
        spectral_flux = np.sqrt(np.sum(np.diff(mel_spec, axis=1)**2, axis=0))
        mean_spectral_flux = float(np.mean(spectral_flux))
        
        return {
            "mean_temporal_variation": mean_temporal_variation,
            "max_temporal_variation": max_temporal_variation,
            "mean_spectral_variation": mean_spectral_variation,
            "phase_coherence": phase_coherence,
            "phase_std": phase_std,
            "energy_entropy": energy_entropy,
            "energy_uniformity": energy_uniformity,
            "mean_band_correlation": mean_band_correlation,
            "mean_spectral_flux": mean_spectral_flux,
        }
    
    def _compute_score(self, features: dict) -> float:
        """
        Compute AI probability from spectro-temporal features.
        
        AI-generated audio typically shows:
        - Lower temporal variation (smoother transitions)
        - Higher energy uniformity (more consistent amplitude)
        - Unusual phase relationships
        - Lower spectral flux (less dynamic spectral changes)
        """
        score = 0.0
        
        # 1. Temporal variation (AI is smoother)
        # Natural: > 15, AI: < 10
        if features["mean_temporal_variation"] < 8.0:
            score += 0.2
        elif features["mean_temporal_variation"] < 12.0:
            score += 0.1
        
        # 2. Energy uniformity (AI is more uniform)
        # Natural: < 0.3, AI: > 0.5
        if features["energy_uniformity"] > 0.6:
            score += 0.25
        elif features["energy_uniformity"] > 0.4:
            score += 0.15
        
        # 3. Phase coherence (AI has different patterns)
        # This is complex, use as moderate signal
        if features["phase_coherence"] < 1.0 or features["phase_coherence"] > 3.0:
            score += 0.15
        
        # 4. Spectral flux (AI has less dynamic changes)
        # Natural: > 20, AI: < 15
        if features["mean_spectral_flux"] < 12.0:
            score += 0.2
        elif features["mean_spectral_flux"] < 18.0:
            score += 0.1
        
        # 5. Band correlation (AI has unusual patterns)
        # Natural: 0.3-0.7, AI: < 0.3 or > 0.8
        if features["mean_band_correlation"] > 0.8 or features["mean_band_correlation"] < 0.25:
            score += 0.2
        
        return min(score, 1.0)
    
    def _estimate_confidence(
        self,
        audio: np.ndarray,
        features: dict,
        sr: int
    ) -> float:
        """Estimate confidence based on signal quality."""
        confidence = 0.65  # Base confidence
        
        # Longer audio = more confident
        duration = len(audio) / sr
        if duration > 5.0:
            confidence += 0.1
        elif duration < 1.0:
            confidence -= 0.2
        
        # Check if features are in decisive ranges
        if features["energy_uniformity"] > 0.6 or features["energy_uniformity"] < 0.2:
            confidence += 0.05
        
        return min(max(confidence, 0.0), 1.0)
