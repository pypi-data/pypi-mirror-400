from typing import Any, Dict, Optional, List, Tuple
import numpy as np
import os
import warnings
import logging
from veridex.core.signal import BaseSignal, DetectionResult
from veridex.utils.downloads import download_file, get_cache_dir

logger = logging.getLogger(__name__)

class RPPGSignal(BaseSignal):
    """
    Detects Deepfakes by analyzing the rPPG (Remote Photoplethysmography) signal.
    Real humans have a heartbeat (0.7-4Hz). Deepfakes often lack this or have noise.
    """

    @property
    def name(self) -> str:
        return "rppg_physnet"

    @property
    def dtype(self) -> str:
        return "video"

    def check_dependencies(self) -> None:
        try:
            import torch
            import cv2
            import scipy.signal
        except ImportError:
            raise ImportError("RPPGSignal requires 'torch', 'opencv-python-headless', and 'scipy'. Install veridex[video].")

    def run(self, input_data: str) -> DetectionResult:
        """
        Args:
            input_data: Path to video file.
        """
        self.check_dependencies()

        try:
            frames = self._load_video_frames(input_data, max_frames=300) # Analyze ~10 sec
            if frames is None or len(frames) < 30:
                return DetectionResult(
                    score=0.5,
                    confidence=0.0,
                    metadata={"error": "Video too short or unreadable"},
                    error="Video read error"
                )

            # Detect and Crop Face (Track first face found)
            faces = self._detect_faces(frames)
            
            # Check if faces is empty or malformed
            if faces is None or len(faces) == 0 or (isinstance(faces, np.ndarray) and faces.size == 0):
                 return DetectionResult(
                    score=0.5,
                    confidence=0.0,
                    metadata={"error": "No face detected"},
                    error="No face detected"
                )

            # Extract BVP Signal - track if using trained weights
            bvp_signal, weights_loaded = self._extract_signal(faces)

            # Analyze PSD
            fake_prob, meta = self._analyze_psd(bvp_signal)
            
            # Calculate confidence based on signal quality and model training status
            peak_ratio = meta.get("peak_ratio", 0.0)
            snr = meta.get("snr", 0.0)
            
            # Base confidence from signal quality
            if peak_ratio > 4.0:
                signal_confidence = 0.85  # Very strong periodic signal
            elif peak_ratio > 3.0:
                signal_confidence = 0.75
            elif peak_ratio > 2.0:
                signal_confidence = 0.65
            elif peak_ratio > 1.5:
                signal_confidence = 0.50
            else:
                signal_confidence = 0.35  # Weak/noisy signal
            
            # Adjust by model training status
            if weights_loaded:
                # Trained model: use higher portion of signal confidence
                confidence = signal_confidence
            else:
                # Untrained model: significantly reduce confidence
                confidence = min(signal_confidence * 0.3, 0.4)  # Cap at 0.4 for untrained

            return DetectionResult(
                score=fake_prob,
                confidence=confidence,
                metadata={**meta, "model_trained": weights_loaded}
            )

        except Exception as e:
            return DetectionResult(score=0.0, confidence=0.0, error=str(e))

    def _load_video_frames(self, path: str, max_frames: int = 300) -> np.ndarray:
        import cv2
        cap = cv2.VideoCapture(path)
        frames = []
        count = 0
        while cap.isOpened() and count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
            count += 1
        cap.release()
        return np.array(frames)

    def _detect_faces(self, frames: np.ndarray) -> List[np.ndarray]:
        from veridex.video.processing import FaceDetector
        detector = FaceDetector()

        # Use the built-in tracking method for temporal consistency
        # Convert np.ndarray frames (T, H, W, C) to list for the detector
        frame_list = [f for f in frames]
        roi_frames = detector.track_faces(frame_list, size=(128, 128))

        return roi_frames # (T, 128, 128, 3)

    def _extract_signal(self, face_frames: np.ndarray) -> tuple[np.ndarray, bool]:
        """Extract BV signal and return whether trained weights were loaded."""
        import torch
        from veridex.video.models.physnet import PhysNet

        # Prepare for model
        tensor = torch.from_numpy(face_frames).float() / 255.0
        tensor = tensor.permute(3, 0, 1, 2) # (C, T, H, W)
        tensor = tensor.unsqueeze(0) # (1, C, T, H, W)

        model = PhysNet()
        model.eval()

        # Load weights from centralized config
        from veridex.video.weights import get_weight_config
        
        weight_config = get_weight_config('physnet')
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
                logger.info(f"✓ Loaded PhysNet weights from {weights_path}")
                weights_loaded = True
             except Exception:
                pass  # Silently fail, final warning below will inform user
        
        if not weights_loaded:
            warnings.warn(
                "⚠ RPPGSignal is using untrained weights. Predictions are random.\n"
                "For production use, download real PhysNet weights.",
                UserWarning,
                stacklevel=2
            )

        with torch.no_grad():
             # Process in chunks if T is too large, but PhysNet is T-conv.
             # T=300 might be big for memory.
             # Let's use a sliding window or just crop to T=128 (approx 4 sec at 30fps)
             T = tensor.shape[2]
             if T > 128:
                 tensor = tensor[:, :, :128, :, :]

             signal = model(tensor) # (1, T)

        return signal.squeeze().numpy(), weights_loaded

    def _analyze_psd(self, signal: np.ndarray) -> Tuple[float, Dict[str, Any]]:
        from scipy import signal as scipy_signal

        # Detrend
        signal = scipy_signal.detrend(signal)

        # PSD
        fs = 30.0 # Assumed FPS
        freqs, psd = scipy_signal.periodogram(signal, fs)

        # ROI: 0.7 Hz (42 BPM) to 4.0 Hz (240 BPM)
        mask = (freqs >= 0.7) & (freqs <= 4.0)
        roi_power = np.trapz(psd[mask], freqs[mask])
        total_power = np.trapz(psd, freqs)

        snr = roi_power / (total_power + 1e-6)

        # Peak analysis
        # If real, there should be a dominant peak in ROI.
        roi_psd = psd[mask]
        if len(roi_psd) > 0:
            peak_power = np.max(roi_psd)
            peak_ratio = peak_power / (np.mean(roi_psd) + 1e-6)
        else:
            peak_ratio = 0.0

        # Scoring:
        # High SNR + High Peak Ratio -> Human (Score 0)
        # Low SNR or Flat -> Fake (Score 1)

        # Let's verify assumptions. Deepfakes have "flat line (noise) or random peaks".
        # If noise -> SNR might be low (energy spread) or high (if random sine wave).
        # Usually, deepfakes have *temporal smoothing*, so the signal is suppressed.
        # So low energy in physiological band relative to DC/LF? Detrend removes DC.

        # Simplified logic:
        # If peak_ratio is high (> 3.0), likely periodic heart beat -> Human.
        # Map peak_ratio 3.0 -> Score 0.0. peak_ratio 1.0 -> Score 1.0.

        # Invert logic for "Fake Prob"
        # score = 1.0 - sigmoid(peak_ratio - threshold)

        score = 1.0 / (1.0 + np.exp(peak_ratio - 2.5)) # Soft threshold around 2.5

        metadata = {
            "snr": float(snr),
            "peak_ratio": float(peak_ratio),
            "dominant_freq": float(freqs[mask][np.argmax(roi_psd)]) if len(roi_psd) > 0 else 0.0
        }

        return float(score), metadata
