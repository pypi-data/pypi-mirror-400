"""
Breathing-based detector for audio deepfakes.

Based on the research "Every Breath You Don't Take: Deepfake Speech Detection Using Breath" (2024).
Real human speech contains natural breathing patterns (inhalations) that are often
missing, unnatural, or misplaced in AI-generated speech (TTS/VC).

This signal analyzes the audio to detect breath events and uses the absence or
irregularity of breathing as a strong indicator of synthetic origin.
"""

from typing import Any, List, Tuple
from pathlib import Path
import numpy as np
from veridex.core.signal import BaseSignal, DetectionResult


class BreathingSignal(BaseSignal):
    """
    Detects AI-generated audio by analyzing breathing patterns.

    Natural speech has regular inhalations (breaths) that have distinct
    spectral and temporal characteristics (broadband noise, specific duration).
    AI models often suppress these or generate them poorly.

    Attributes:
        name (str): 'breathing_audio_detector'
        dtype (str): 'audio'
    """

    def __init__(self, target_sr: int = 16000):
        self.target_sr = target_sr

    @property
    def name(self) -> str:
        return "breathing_audio_detector"

    @property
    def dtype(self) -> str:
        return "audio"

    def check_dependencies(self) -> None:
        try:
            import librosa
            import scipy
        except ImportError:
            raise ImportError(
                "Breathing detector requires 'librosa' and 'scipy'. "
                "Install with: pip install veridex[audio]"
            )

    def run(self, input_data: Any) -> DetectionResult:
        """
        Analyze audio for breathing patterns.

        Args:
            input_data: Path to audio file.

        Returns:
            DetectionResult with score (high score = AI), confidence, and metadata.
        """
        if not isinstance(input_data, (str, Path)):
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error="Input must be a file path"
            )

        try:
            self.check_dependencies()
        except ImportError as e:
            return DetectionResult(score=0.0, confidence=0.0, error=str(e))

        try:
            from veridex.audio.utils import load_audio, validate_audio
            import librosa

            # Load audio
            audio, sr = load_audio(input_data, target_sr=self.target_sr)

            # Validate
            is_valid, error_msg = validate_audio(audio, sr)
            if not is_valid:
                return DetectionResult(score=0.0, confidence=0.0, error=error_msg)

            # Detect breaths
            breaths = self._detect_breaths(audio, sr)

            # Compute features
            metrics = self._compute_breath_metrics(breaths, len(audio)/sr)

            # Compute score
            score = self._compute_score(metrics)

            # Compute confidence
            confidence = self._compute_confidence(metrics, len(audio)/sr)

            return DetectionResult(
                score=score,
                confidence=confidence,
                metadata=metrics
            )

        except Exception as e:
            return DetectionResult(score=0.0, confidence=0.0, error=f"Breathing detection failed: {e}")

    def _detect_breaths(self, audio: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """
        Detect potential breath segments.

        Breaths are characterized by:
        - Low to medium energy (silence < breath < speech)
        - High spectral centroid (high frequency noise)
        - Specific duration (typically 0.1s to 0.8s)
        """
        import librosa

        # 1. Feature Extraction
        hop_length = 512
        frame_length = 2048

        # RMS Energy
        rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]

        # Spectral Centroid
        centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=frame_length, hop_length=hop_length)[0]

        # Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y=audio, frame_length=frame_length, hop_length=hop_length)[0]

        # 2. Thresholding
        # Heuristics for breath detection (simplified from literature)

        # Normalize features
        rms_norm = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-9)

        # Breaths usually have low energy but not absolute silence
        # Speech has high energy
        # Silence has near zero energy

        # Masks
        # 1. Energy window: Not too loud (speech), not too quiet (silence)
        # These thresholds are heuristic and might need tuning
        is_breath_energy = (rms_norm > 0.01) & (rms_norm < 0.2)

        # 2. High frequency content (breaths are hissy)
        # Centroid usually > 2000Hz-3000Hz for breaths
        is_breath_freq = (centroid > 2500)

        # 3. High Zero Crossing Rate
        is_breath_zcr = (zcr > 0.1)

        # Combine
        is_breath_frame = is_breath_energy & is_breath_freq & is_breath_zcr

        # 3. Group frames into segments
        breaths = []
        in_breath = False
        start_frame = 0
        min_breath_frames = int(0.15 * sr / hop_length) # Min 150ms
        max_breath_frames = int(1.2 * sr / hop_length)  # Max 1.2s

        for i, is_breath in enumerate(is_breath_frame):
            if is_breath and not in_breath:
                in_breath = True
                start_frame = i
            elif not is_breath and in_breath:
                in_breath = False
                duration_frames = i - start_frame

                if min_breath_frames <= duration_frames <= max_breath_frames:
                    # Convert to seconds
                    start_time = start_frame * hop_length / sr
                    end_time = i * hop_length / sr
                    breaths.append((start_time, end_time))

        return breaths

    def _compute_breath_metrics(self, breaths: List[Tuple[float, float]], duration: float) -> dict:
        """Compute statistics about detected breaths."""
        num_breaths = len(breaths)
        total_breath_duration = sum(end - start for start, end in breaths)

        bpm = (num_breaths / duration) * 60 if duration > 0 else 0
        breath_ratio = total_breath_duration / duration if duration > 0 else 0
        avg_breath_duration = total_breath_duration / num_breaths if num_breaths > 0 else 0

        # Calculate regularity (std dev of intervals)
        intervals = []
        for i in range(len(breaths) - 1):
            intervals.append(breaths[i+1][0] - breaths[i][1]) # End of one to start of next

        interval_std = float(np.std(intervals)) if len(intervals) > 1 else 0.0

        return {
            "num_breaths": num_breaths,
            "breaths_per_minute": bpm,
            "breath_ratio": breath_ratio,
            "avg_breath_duration": avg_breath_duration,
            "interval_std": interval_std,
            "duration": duration,
            "breaths": breaths # List of (start, end)
        }

    def _compute_score(self, metrics: dict) -> float:
        """
        Compute AI probability score.

        Hypothesis:
        - AI speech (especially older or standard TTS) often lacks breaths entirely -> High Score.
        - Or breaths are very regular/robotic (low interval std) -> Medium Score.
        - Human speech has natural, semi-regular breathing -> Low Score.
        """
        duration = metrics["duration"]
        bpm = metrics["breaths_per_minute"]

        # If very short audio, unreliable
        if duration < 3.0:
            return 0.5 # Neutral

        score = 0.0

        # 1. Lack of breaths (The strongest signal for many TTS)
        # Humans typically breathe 10-20 times per minute in conversation,
        # but in reading/acting it varies.
        # < 2 BPM is very suspicious for continuous speech > 10s
        if bpm < 1.0:
            score = 0.95
        elif bpm < 3.0:
            score = 0.8
        elif bpm < 5.0:
            score = 0.6
        else:
            # 2. Too many breaths (Hyper-breathing deepfakes exist but rare)
            if bpm > 40:
                score = 0.7
            else:
                score = 0.1 # Likely human

        return score

    def _compute_confidence(self, metrics: dict, duration: float) -> float:
        """Estimate confidence in the detection."""
        confidence = 0.7 # Base

        # Short audio is hard to judge for breathing patterns
        if duration < 5.0:
            confidence = 0.3
        elif duration < 10.0:
            confidence = 0.5
        elif duration > 20.0:
            confidence = 0.9

        return confidence
