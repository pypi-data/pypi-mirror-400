from typing import List, Tuple, Optional, Literal
import numpy as np
import warnings

FaceBackend = Literal['haar', 'mediapipe', 'auto']

class FaceDetector:
    """
    Multi-backend face detector with automatic fallback.
    
    Backends (in order of accuracy):
    1. MediaPipe (best, requires mediapipe package)
    2. Haar Cascades (fast, less accurate)
    
    Args:
        backend: 'auto' (try MediaPipe then Haar), 'mediapipe', or 'haar'
    """
    def __init__(self, backend: FaceBackend = 'auto'):
        try:
            import cv2
            self.cv2 = cv2
        except ImportError:
            raise ImportError("FaceDetector requires 'opencv-python-headless'. Please install veridex[video].")
        
        self.backend = backend
        
        if backend == 'auto':
            # Try MediaPipe first, fallback to Haar
            try:
                import mediapipe as mp
                self.backend = 'mediapipe'
                self._init_mediapipe()
            except (ImportError, AttributeError):
                warnings.warn(
                    "MediaPipe not installed or broken. Using Haar Cascades (lower accuracy).\n"
                    "For better face detection: pip install mediapipe",
                    UserWarning
                )
                self.backend = 'haar'
                self._init_haar()
        elif backend == 'mediapipe':
            self._init_mediapipe()
        elif backend == 'haar':
            self._init_haar()
        else:
            raise ValueError(f"Unknown backend: {backend}. Use 'auto', 'mediapipe', or 'haar'")
    
    def _init_mediapipe(self):
        """Initialize MediaPipe Face Detection."""
        import mediapipe as mp
        self.mp_face_detection = mp.solutions.face_detection
        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0=short range (<2m), 1=full range
            min_detection_confidence=0.5
        )
        
    def _init_haar(self):
        """Initialize Haar Cascade Face Detection."""
        cascade_path = self.cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.detector = self.cv2.CascadeClassifier(cascade_path)

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a frame.

        Args:
            frame: RGB or BGR numpy array (OpenCV uses BGR).

        Returns:
            List of (x, y, w, h) tuples.
        """
        if self.backend == 'mediapipe':
            return self._detect_mediapipe(frame)
        else:
            return self._detect_haar(frame)
    
    def _detect_mediapipe(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces using MediaPipe."""
        # MediaPipe expects RGB
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            # Assume BGR from OpenCV, convert to RGB
            frame_rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        else:
            frame_rgb = frame
            
        results = self.detector.process(frame_rgb)
        
        if not results.detections:
            return []
        
        h, w = frame.shape[:2]
        bboxes = []
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            box_w = int(bbox.width * w)
            box_h = int(bbox.height * h)
            bboxes.append((x, y, box_w, box_h))
        
        return bboxes
    
    def _detect_haar(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces using Haar Cascades."""
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=self.cv2.CASCADE_SCALE_IMAGE
        )
        return [tuple(f) for f in faces]

    def extract_face(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], size: Tuple[int, int] = (128, 128)) -> np.ndarray:
        """
        Extract and resize the face ROI.
        """
        x, y, w, h = bbox
        # Ensure bounds
        h_img, w_img = frame.shape[:2]
        x = max(0, x)
        y = max(0, y)
        w = min(w, w_img - x)
        h = min(h, h_img - y)
        
        face = frame[y:y+h, x:x+w]
        if face.size == 0 or w == 0 or h == 0:
            return np.zeros((size[1], size[0], 3), dtype=frame.dtype)
        return self.cv2.resize(face, size)

    def track_faces(self, frames: List[np.ndarray], size: Tuple[int, int] = (128, 128)) -> np.ndarray:
        """
        Track and extract a single face across a sequence of frames.
        Uses simple IoU tracking and 'largest face' initialization.
        """
        roi_frames = []
        if not frames:
            return np.array(roi_frames)

        # 1. Init on first frame
        current_bbox = None
        
        # Try finding face in first few frames if missing in 0
        for i, frame in enumerate(frames):
            dets = self.detect(frame)
            if dets:
                # Pick largest
                current_bbox = max(dets, key=lambda b: b[2] * b[3])
                break
        
        if current_bbox is None:
            # No face found in entire video (or start)
            # Return zeros
            return np.zeros((len(frames), size[1], size[0], 3), dtype=np.uint8)

        # Backfill missing start
        for _ in range(i):
             roi_frames.append(self.extract_face(frames[0], current_bbox, size))

        # 2. Track
        for frame in frames[i:]:
            dets = self.detect(frame)
            if not dets:
                # Lost detection, keep previous bbox
                pass 
            else:
                # Find bbox with best overlap (IoU) with current_bbox
                best_iou = -1.0
                best_box = None
                
                cx, cy, cw, ch = current_bbox
                c_area = cw * ch
                
                for box in dets:
                    bx, by, bw, bh = box
                    # IoU calc
                    ix = max(cx, bx)
                    iy = max(cy, by)
                    iw = min(cx+cw, bx+bw) - ix
                    ih = min(cy+ch, by+bh) - iy
                    
                    if iw > 0 and ih > 0:
                        inter = iw * ih
                        union = c_area + (bw * bh) - inter
                        iou = inter / union
                        if iou > best_iou:
                            best_iou = iou
                            best_box = box
                
                if best_box is not None and best_iou > 0.1: # Threshold for tracking drift
                    current_bbox = best_box
                else:
                    # If all detections are far away, it might be a new face or false positive.
                    # For RPPG we usually want to STICK to the subject.
                    # Keep previous bbox.
                    pass
            
            # Extract
            roi_frames.append(self.extract_face(frame, current_bbox, size))
            
        return np.array(roi_frames)
