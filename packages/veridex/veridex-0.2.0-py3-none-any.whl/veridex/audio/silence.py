from typing import Any
import numpy as np
from veridex.core.signal import BaseSignal, DetectionResult

class SilenceSignal(BaseSignal):
    """
    Analyzes silence intervals (pauses) in speech audio.
    
    Synthetic speech (TTS) often has regular, unnatural, or non-existent pauses compared to natural speech.
    This signal calculates the ratio of silence to total audio duration and the variance of silence durations.
    """

    @property
    def name(self) -> str:
        return "silence_analysis"

    @property
    def dtype(self) -> str:
        return "audio"
        
    def check_dependencies(self) -> None:
        try:
            import librosa
        except ImportError:
            raise ImportError("librosa is required for SilenceSignal. Install veridex[audio].")

    def run(self, input_data: Any) -> DetectionResult:
        """
        Runs silence analysis on the input audio file path or numpy array.
        """
        try:
            self.check_dependencies()
            import librosa
            if isinstance(input_data, str):
                y, sr = librosa.load(input_data, sr=None)
            elif isinstance(input_data, tuple):
                # Assume (y, sr) tuple
                y, sr = input_data
            else:
                 return DetectionResult(
                    score=0.0,
                    confidence=0.0,
                    error="Input must be a file path or (y, sr) tuple."
                )

            # Detect non-silent intervals
            # top_db: The threshold (in decibels) below reference to consider as silence
            non_silent_intervals = librosa.effects.split(y, top_db=20)
            
            if len(non_silent_intervals) == 0:
                 return DetectionResult(
                    score=0.0, # Cannot determine
                    confidence=0.0,
                    explanation="Audio is completely silent."
                )

            total_duration = len(y) / sr
            
            # Calculate total non-silent duration
            non_silent_duration = sum([(end - start) for start, end in non_silent_intervals]) / sr
            silence_duration = total_duration - non_silent_duration
            silence_ratio = silence_duration / total_duration
            
            # Analyze pause lengths (gaps between intervals)
            pause_lengths = []
            for i in range(len(non_silent_intervals) - 1):
                # End of current minus start of next
                pause_samples = non_silent_intervals[i+1][0] - non_silent_intervals[i][1]
                pause_lengths.append(pause_samples / sr)
            
            if pause_lengths:
                mean_pause = np.mean(pause_lengths)
                std_pause = np.std(pause_lengths)
            else:
                mean_pause = 0.0
                std_pause = 0.0

            # Heuristic:
            # - Very low silence ratio -> typically synthetic (early TTS)
            # - Very low variance in pause lengths -> synthetic (robotic pacing)
            
            # Simple score: if silence ratio is very low (< 5%), likely AI.
            # Using a gaussian-like drop off? Let's keep it simple linear for now.
            
            is_suspiciously_continuous = 1.0 if silence_ratio < 0.05 else 0.0
            
            # If standard deviation of pauses is very low (e.g. < 0.05s), it's robotic
            is_robotic_pacing = 1.0 if (len(pause_lengths) > 2 and std_pause < 0.05) else 0.0
            
            score = max(is_suspiciously_continuous, is_robotic_pacing)
            
            # Confidence based on amount of evidence
            # More pauses analyzed = higher confidence
            if len(pause_lengths) > 10:
                base_confidence = 0.45
            elif len(pause_lengths) > 5:
                base_confidence = 0.4
            else:
                base_confidence = 0.35
            
            # Boost confidence if signal is strong (clear detection)
            if score > 0.5:
                confidence = min(base_confidence + 0.05, 0.5)
            else:
                confidence = base_confidence

            return DetectionResult(
                score=score,
                confidence=confidence,
                metadata={
                    "silence_ratio": float(silence_ratio),
                    "mean_pause_duration": float(mean_pause),
                    "pause_duration_std": float(std_pause),
                    "total_duration": float(total_duration),
                    "num_pauses": len(pause_lengths)
                }
            )
            
        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error=f"Silence analysis failed: {str(e)}"
            )
