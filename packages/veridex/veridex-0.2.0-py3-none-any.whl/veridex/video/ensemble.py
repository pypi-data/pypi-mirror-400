"""Ensemble fusion for video deepfake detection."""
from typing import List, Optional
import numpy as np
import warnings
from veridex.core.signal import BaseSignal, DetectionResult


class VideoEnsemble(BaseSignal):
    """
    Ensemble of video deepfake detection signals.
    Combines RPPG, I3D, and LipSync using weighted fusion.
    
    Example:
        >>> from veridex.video import VideoEnsemble
        >>> ensemble = VideoEnsemble()
        >>> result = ensemble.run("video.mp4")
        >>> print(f"Combined score: {result.score:.2f}")
    """
    
    @property
    def name(self) -> str:
        return "video_ensemble"
    
    @property
    def dtype(self) -> str:
        return "video"
    
    def __init__(self, signals: Optional[List[BaseSignal]] = None):
        """
        Args:
            signals: List of signals to ensemble. Defaults to all three video signals.
        """
        if signals is None:
            # Import here to avoid circular dependency
            from veridex.video.rppg import RPPGSignal
            from veridex.video.i3d import I3DSignal
            from veridex.video.lipsync import LipSyncSignal
            
            self.signals = [
                RPPGSignal(),
                I3DSignal(),
                LipSyncSignal()
            ]
        else:
            self.signals = signals
    
    def check_dependencies(self) -> None:
        """Check dependencies for all signals."""
        for signal in self.signals:
            signal.check_dependencies()
    
    def run(self, input_data: str) -> DetectionResult:
        """
        Run all signals and fuse results using weighted average.
        
        Args:
            input_data: Path to video file
            
        Returns:
            DetectionResult with fused score and metadata from all signals
        """
        results = []
        
        for signal in self.signals:
            try:
                result = signal.run(input_data)
                # Only include successful results (no error)
                if result.error is None and result.confidence > 0:
                    results.append((signal.name, result))
            except Exception as e:
                # Log but continue with other signals
                warnings.warn(
                    f"{signal.name} failed: {e}. Continuing with other signals.",
                    UserWarning
                )
        
        if not results:
            return DetectionResult(
                score=0.5,
                confidence=0.0,
                error="All signals failed to produce valid results",
                metadata={"num_successful": 0, "num_total": len(self.signals)}
            )
        
        # Weighted average (confidence as weight)
        total_weight = sum(r.confidence for _, r in results)
        
        if total_weight == 0:
            # All zero confidence, use simple average
            avg_score = float(np.mean([r.score for _, r in results]))
            avg_conf = 0.0
        else:
            avg_score = sum(r.score * r.confidence for _, r in results) / total_weight
            avg_conf = total_weight / len(self.signals)  # Normalize by total signals
        
        # Build metadata
        individual_results = {}
        for sig_name, result in results:
            individual_results[sig_name] = {
                "score": float(result.score),
                "confidence": float(result.confidence),
                "metadata": result.metadata
            }
        
        return DetectionResult(
            score=float(avg_score),
            confidence=float(avg_conf),
            metadata={
                "individual_results": individual_results,
                "num_successful": len(results),
                "num_total": len(self.signals),
                "fusion_method": "weighted_average"
            }
        )
