from typing import Any, Dict, Optional
import numpy as np
import os
import warnings
import logging
from veridex.core.signal import BaseSignal, DetectionResult

logger = logging.getLogger(__name__)

class LipSyncSignal(BaseSignal):
    """
    Detects Deepfakes by checking Audio-Visual Synchronization (Lip-Sync).
    Uses SyncNet logic.
    """

    @property
    def name(self) -> str:
        return "lipsync_wav2lip"

    @property
    def dtype(self) -> str:
        return "video"

    def check_dependencies(self) -> None:
        try:
            import torch
            import cv2
            import librosa
        except ImportError:
            raise ImportError("LipSyncSignal requires 'torch', 'opencv', and 'librosa'. Install veridex[video].")

    def run(self, input_data: str) -> DetectionResult:
        self.check_dependencies()
        try:
            # 1. Load Audio and Video segments
            # For robustness, we check the AV offset on multiple random 0.2s clips

            offsets = []
            weights_loaded_flags = []
            for _ in range(3): # Check 3 segments
                offset, weights_loaded = self._calculate_av_offset(input_data)
                if offset is not None:
                    offsets.append(offset)
                    weights_loaded_flags.append(weights_loaded)

            if not offsets:
                 return DetectionResult(score=0.5, confidence=0.0, error="Could not extract AV segments")

            avg_offset = sum(offsets) / len(offsets)
            offset_variance = np.var(offsets) if len(offsets) > 1 else 0.0
            any_weights_loaded = any(weights_loaded_flags)

            # Metric:
            # Offset is Euclidean distance between Audio and Video embeddings.
            # Small distance -> Sync -> Real.
            # Large distance -> Out of Sync -> Fake.
            # Real < 0.8 (heuristic threshold).

            score = 0.0
            threshold = 0.8
            if avg_offset > threshold:
                # Map distance to probability.
                score = min((avg_offset - threshold) / 1.0, 1.0)
            
            # Calculate confidence from measurement consistency and model status
            # Low variance in offsets = consistent measurement = high confidence
            if offset_variance < 0.05:
                measurement_confidence = 0.85  # Very consistent
            elif offset_variance < 0.1:
                measurement_confidence = 0.75
            elif offset_variance < 0.2:
                measurement_confidence = 0.65
            else:
                measurement_confidence = 0.45  # High variance, less reliable
            
            # Adjust by model training status
            if any_weights_loaded:
                confidence = measurement_confidence
            else:
                # Untrained model: reduce confidence significantly
                confidence = min(measurement_confidence * 0.35, 0.4)

            return DetectionResult(
                score=score,
                confidence=confidence,
                metadata={
                    "av_distance": avg_offset,
                    "offset_variance": offset_variance,
                    "num_segments": len(offsets),
                    "model_trained": any_weights_loaded
                }
            )

        except Exception as e:
            return DetectionResult(score=0.0, confidence=0.0, error=str(e))

    def _calculate_av_offset(self, path: str) -> tuple[Optional[float], bool]:
        """Calculate AV offset and return whether trained weights were loaded."""
        import torch
        import librosa
        import cv2
        from veridex.video.models.syncnet import SyncNet
        from veridex.video.processing import FaceDetector
        from veridex.utils.downloads import download_file, get_cache_dir

        # 1. Load Audio (0.2s segment)
        try:
            y, sr = librosa.load(path, sr=16000)
        except Exception:
            return None, False

        if len(y) < 16000: # Need at least 1 sec to find a good chunk
            return None, False

        # Pick a random start point
        import random
        start_sec = random.uniform(0, len(y)/sr - 0.3)
        start_sample = int(start_sec * sr)
        # 0.2s duration for SyncNet
        duration_samples = int(0.2 * sr)
        audio_chunk = y[start_sample : start_sample + duration_samples]

        # MFCC: 13 coeffs, window 25ms, hop 10ms
        # SyncNet expects specific MFCC shape.
        # (1, 1, 13, 20) -> 13 MFCCs over 20 timesteps (20*10ms = 200ms)
        mfcc = librosa.feature.mfcc(y=audio_chunk, sr=sr, n_mfcc=13, n_fft=400, hop_length=160)
        if mfcc.shape[1] < 20:
             mfcc = np.pad(mfcc, ((0,0), (0, 20-mfcc.shape[1])))
        mfcc = mfcc[:, :20]

        # 2. Load Video (5 frames corresponding to that 0.2s)
        # 0.2s at 25fps = 5 frames.
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 25

        start_frame = int(start_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        frames = []
        for _ in range(5):
            ret, frame = cap.read()
            if not ret: break
            frames.append(frame)
        cap.release()

        if len(frames) < 5:
            return None, False

        # 3. Detect and Crop Mouth
        # Simplified: Detect face, take lower half.
        detector = FaceDetector()
        face_crops = []
        for frame in frames:
            dets = detector.detect(frame)
            if not dets:
                # Fallback: center crop? Or just fail this segment
                return None, False

            # Largest face
            face = max(dets, key=lambda b: b[2] * b[3])
            x, y, w, h = face

            # Mouth region approximation (lower half of face)
            mouth_y = y + h // 2
            mouth_h = h // 2

            mouth_crop = detector.extract_face(frame, (x, mouth_y, w, mouth_h), size=(112, 112))
            face_crops.append(mouth_crop)

        # Stack frames
        # Input: (B, 15, 112, 112). 15 channels = 5 frames * 3 colors.
        # face_crops: 5 * (112, 112, 3)
        video_tensor = np.concatenate(face_crops, axis=2) # (112, 112, 15)

        # To Torch
        audio_t = torch.from_numpy(mfcc).float().unsqueeze(0).unsqueeze(0) # (1, 1, 13, 20)
        video_t = torch.from_numpy(video_tensor).float().permute(2, 0, 1).unsqueeze(0) # (1, 15, 112, 112)

        # 4. Inference
        model = SyncNet()
        model.eval()

        # Load weights from centralized config
        from veridex.video.weights import get_weight_config
        
        weight_config = get_weight_config('syncnet')
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
                # Note: Official weights might be LuaTorch or different format.
                # This assumes a PyTorch converted version or compatible dict.
                model.load_state_dict(torch.load(weights_path, map_location='cpu'))
                logger.info(f"✓ Loaded SyncNet weights from {weights_path}")
                weights_loaded = True
             except Exception:
                pass  # Silently fail, final warning below will inform user
        
        if not weights_loaded:
            warnings.warn(
                "⚠ LipSyncSignal is using untrained weights. Predictions are random.\n"
                "For production use, download real SyncNet weights from VGG.",
                UserWarning,
                stacklevel=2
            )

        with torch.no_grad():
            a_emb, v_emb = model(audio_t, video_t)
            dist = torch.norm(a_emb - v_emb, p=2, dim=1).item()

        return dist, weights_loaded
