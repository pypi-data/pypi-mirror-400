from typing import Any, Dict, Optional
import numpy as np
import os
import warnings
import logging
from veridex.core.signal import BaseSignal, DetectionResult

logger = logging.getLogger(__name__)

class I3DSignal(BaseSignal):
    """
    Detects Deepfakes using Spatiotemporal features (I3D).
    """

    @property
    def name(self) -> str:
        return "spatiotemporal_i3d"

    @property
    def dtype(self) -> str:
        return "video"

    def check_dependencies(self) -> None:
        try:
            import torch
            import cv2
        except ImportError:
            raise ImportError("I3DSignal requires 'torch' and 'opencv-python-headless'. Install veridex[video].")

    def run(self, input_data: str) -> DetectionResult:
        self.check_dependencies()
        try:
            # 1. Load Video Clip (Fixed size for I3D, e.g., 64 frames)
            clip = self._load_clip(input_data, frames_needed=64)
            if clip is None:
                return DetectionResult(score=0.5, confidence=0.0, error="Video too short")

            # 2. Run Inference
            score, weights_loaded = self._run_inference(clip)
            
            # 3. Calculate confidence based on model certainty and training status
            # Distance from 0.5 (uncertainty point) indicates model confidence
            distance_from_uncertain = abs(score - 0.5)
            
            # Map distance to model confidence
            # Distance 0.5 (max, score at 0 or 1) -> very confident
            # Distance 0.0 (score at 0.5) -> very uncertain
            model_confidence = min(distance_from_uncertain * 2, 1.0)  # Scale to [0, 1]
            
            # Boost base confidence for I3D (sophisticated spatiotemporal model)
            if model_confidence > 0.7:
                base_confidence = 0.90
            elif model_confidence > 0.5:
                base_confidence = 0.85
            elif model_confidence > 0.3:
                base_confidence = 0.75
            else:
                base_confidence = 0.65
            
            # Adjust by training status
            if weights_loaded:
                confidence = base_confidence
            else:
                # Untrained weights: very low confidence
                confidence = min(base_confidence * 0.15, 0.25)

            return DetectionResult(
                score=score,
                confidence=confidence,
                metadata={
                    "frames": 64,
                    "model_confidence": model_confidence,
                    "model_trained": weights_loaded
                }
            )

        except Exception as e:
            return DetectionResult(score=0.0, confidence=0.0, error=str(e))

    def _load_clip(self, path: str, frames_needed: int) -> Optional[np.ndarray]:
        import cv2
        cap = cv2.VideoCapture(path)
        frames = []
        while cap.isOpened() and len(frames) < frames_needed:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (224, 224))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
        cap.release()

        if len(frames) < frames_needed:
            # Pad or fail
            return None

        return np.array(frames) # (T, H, W, C)

    def _run_inference(self, clip: np.ndarray) -> tuple[float, bool]:
        """Run I3D inference and return score and whether trained weights were loaded."""
        import torch
        from veridex.video.models.i3d import InceptionI3D

        # Preprocess
        tensor = torch.from_numpy(clip).float() / 255.0 * 2 - 1 # [-1, 1]
        tensor = tensor.permute(3, 0, 1, 2) # (C, T, H, W)
        tensor = tensor.unsqueeze(0) # (1, C, T, H, W)

        model = InceptionI3D(num_classes=1)
        model.eval()

        # Load weights from centralized config
        from veridex.utils.downloads import get_cache_dir, download_file
        from veridex.video.weights import get_weight_config

        weight_config = get_weight_config('i3d')
        weights_url = weight_config['url']
        weights_path = os.path.join(get_cache_dir(), weight_config['filename'])
        sha256 = weight_config.get('sha256')

        weights_loaded = False
        if not os.path.exists(weights_path):
            try:
                download_file(weights_url, weights_path)
            except Exception:
                pass  # Silently fail, final warning below will inform user

        if os.path.exists(weights_path):
             try:
                model.load_state_dict(torch.load(weights_path, map_location='cpu'))
                logger.info(f"✓ Loaded I3D weights from {weights_path}")
                weights_loaded = True
             except Exception:
                pass  # Silently fail, final warning below will inform user
        
        if not weights_loaded:
            warnings.warn(
                "⚠ I3DSignal is using untrained weights. Predictions are random.\\n"
                "For production use, download real I3D weights trained on Kinetics-400.",
                UserWarning,
                stacklevel=2
            )

        with torch.no_grad():
            logits = model(tensor) # (1, 1, T_out)
            # Average over time dimension
            logit = logits.mean()
            prob = torch.sigmoid(logit).item()

        return prob, weights_loaded
