# Video Deepfake Detection Guide

## Overview

Veridex provides state-of-the-art video deepfake detection through three specialized signals that analyze different aspects of video authenticity:

- **RPPGSignal**: Detects biological heartbeat signals
- **I3DSignal**: Analyzes spatiotemporal motion patterns
- **LipSyncSignal**: Checks audio-visual synchronization
- **VideoEnsemble**: Combines all three for robust detection

---

## Quick Start

### Installation

```bash
# Install video detection support
pip install veridex[video]
```

### Basic Usage

```python
from veridex.video import VideoEnsemble

# Create ensemble detector
ensemble = VideoEnsemble()

# Analyze video
result = ensemble.run("video.mp4")

print(f"AI Probability: {result.score:.2%}")
print(f"Confidence: {result.confidence:.2%}")
```

---

## Understanding the Signals

### 1. RPPGSignal (Biological Analysis)

**What it does**: Extracts the remote photoplethysmography (rPPG) signal from facial video to detect heartbeat patterns.

**How it works**:
1. Detects and tracks the face across frames
2. Extracts subtle color changes from skin regions
3. Analyzes the frequency spectrum for biological rhythms (0.7-4 Hz)
4. Computes SNR (signal-to-noise ratio) of the heartbeat signal

**Strengths**:
- ✅ Very effective for face-swap deepfakes
- ✅ Biological signals are hard to fake
- ✅ No GPU required

**Limitations**:
- ❌ Requires clear face visibility
- ❌ Fails on animated/CGI content
- ❌ Sensitive to lighting and motion

**When to use**: Face-focused deepfakes (face-swap, face reenactment)

**Example**:
```python
from veridex.video import RPPGSignal

detector = RPPGSignal()
result = detector.run("face_video.mp4")

print(f"Heartbeat SNR: {result.metadata['snr']:.2f}")
```

---

### 2. I3DSignal (Spatiotemporal Analysis)

**What it does**: Analyzes motion and temporal patterns using 3D convolutional networks.

**How it works**:
1. Samples 64 consecutive frames
2. Processes through Inception-3D architecture
3. Learns spatiotemporal features indicating synthetic generation

**Strengths**:
- ✅ Works on full-frame videos
- ✅ Doesn't require face detection
- ✅ Effective on various deepfake types

**Limitations**:
- ❌ Needs at least 64 frames (~2 seconds at 30fps)
- ❌ Currently using untrained weights (random predictions)
- ❌ GPU recommended for real-time performance

**When to use**: General-purpose video deepfake detection

**Example**:
```python
from veridex.video import I3DSignal

detector = I3DSignal()
result = detector.run("video.mp4")

print(f"AI Score: {result.score:.2%}")
```

---

### 3. LipSyncSignal (Audio-Visual Synchronization)

**What it does**: Checks if audio and visual streams are properly synchronized.

**How it works**:
1. Extracts audio waveform (MFCC features)
2. Extracts mouth region frames
3. Computes audio and video embeddings with SyncNet
4. Measures AV offset distance

**Strengths**:
- ✅ Effective for dubbed/lip-synced fakes
- ✅ Detects audio-video manipulation
- ✅ No GPU required

**Limitations**:
- ❌ Requires both audio and video
- ❌ Needs clear mouth visibility
- ❌ Can fail on silent videos

**When to use**: Suspected audio manipulation, voice cloning with video

**Example**:
```python
from veridex.video import LipSyncSignal

detector = LipSyncSignal()
result = detector.run("talking_video.mp4")

print(f"AV Sync Score: {result.score:.2%}")
```

---

## VideoEnsemble: Recommended Approach

The `VideoEnsemble` combines all three signals using weighted averaging for maximum robustness.

### How It Works

1. **Run all signals** in parallel
2. **Filter failures** (gracefully handle signal errors)
3. **Weighted fusion** (confidence-based averaging)
4. **Return combined result** with individual breakdowns

### Advantages

- ✅ More robust than individual signals
- ✅ Graceful degradation (works even if some signals fail)
- ✅ Provides detailed breakdown
- ✅ Confidence-weighted fusion

### Example

```python
from veridex.video import VideoEnsemble

ensemble = VideoEnsemble()
result = ensemble.run("suspicious_video.mp4")

# Overall result
print(f"Combined Score: {result.score:.2%}")
print(f"Confidence: {result.confidence:.2%}")

# Individual results
for signal_name, signal_result in result.metadata['individual_results'].items():
    print(f"{signal_name}: {signal_result['score']:.2%}")
```

---

## Advanced Configuration

### Using Custom Model Weights

```python
from veridex.video.weights import set_weight_url

# Override default weight URLs
set_weight_url('physnet', 'https://my-server.com/physnet.pth')
set_weight_url('i3d', 'https://my-server.com/i3d.pth')
set_weight_url('syncnet', 'https://my-server.com/syncnet.pth')
```

### Environment Variables

```bash
# Override weight URLs via environment
export VERIDEX_PHYSNET_URL="https://my-server.com/physnet.pth"
export VERIDEX_I3D_URL="https://my-server.com/i3d.pth"
export VERIDEX_SYNCNET_URL="https://my-server.com/syncnet.pth"
```

### Face Detection Backend Selection

```python
from veridex.video.processing import FaceDetector

# Auto-select best available (default)
detector = FaceDetector('auto')  # MediaPipe if available, else Haar

# Force specific backend
detector = FaceDetector('mediapipe')  # Best accuracy
detector = FaceDetector('haar')       # Lightweight
```

---

## Best Practices

### 1. **Use Ensemble for Production**
Always prefer `VideoEnsemble` over individual signals for maximum reliability.

### 2. **Check Confidence Scores**
A high score with low confidence is unreliable. Always check:
```python
if result.confidence < 0.5:
    print("⚠️ Low confidence - manual review recommended")
```

### 3. **Handle Edge Cases**
```python
from veridex.video.utils import validate_video_file

# Pre-validate video
valid, error, metadata = validate_video_file("video.mp4")
if not valid:
    print(f"Invalid video: {error}")
else:
    print(f"Duration: {metadata['duration_seconds']}s")
    # Proceed with detection...
```

### 4. **Process Long Videos Efficiently**
```python
from veridex.video.utils import chunk_video_frames
import numpy as np
import cv2

# Load video
cap = cv2.VideoCapture("long_video.mp4")
frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()
frames = np.array(frames)

# Process in chunks
for start, chunk in chunk_video_frames(frames, chunk_size=300, overlap=30):
    # Process each chunk
    result = process_chunk(chunk)
```

---

## Current Limitations

> [!WARNING]
> **Model Weights Not Yet Available**
> 
> The video module currently uses **placeholder/untrained weights**. Predictions are essentially random until real pre-trained weights are integrated.
> 
> **To add real weights**:
> 1. Obtain pre-trained PhysNet, I3D (Kinetics-400), and SyncNet weights
> 2. Host them on a stable server
> 3. Update URLs in `veridex/video/weights.py`

### Known Issues

- **RPPG**: May fail on videos without clear faces or in poor lighting
- **I3D**: Requires minimum 64 frames (padded if shorter)
- **LipSync**: Requires both audio and video, fails on silent content
- **All signals**: Accuracy depends on real pre-trained weights

### Face Detection

- MediaPipe (recommended): ~90% recall, requires installation
- Haar Cascades (fallback): ~60% recall, lighter weight
- No face = RPPG and LipSync will fail, but I3D still works

---

## Troubleshooting

### "MediaPipe not installed" warning

```bash
# Already included in video dependencies
# If you see this, reinstall:
pip install --force-reinstall veridex[video]
```

### "Using untrained weights" warning

This is expected. The module is waiting for real pre-trained weights. See [Current Limitations](#current-limitations).

### "No face detected" error

- Ensure video has clear, frontal faces
- Check lighting conditions
- Try a different face detection backend (`mediapipe` vs `haar`)
- Use I3D signal instead (doesn't require faces)

### Audio loading errors

LipSync requires valid audio. For silent videos, use RPPG or I3D instead:

```python
from veridex.video import RPPGSignal, I3DSignal

# Use signals that don't need audio
rppg = RPPGSignal()
i3d = I3DSignal()
```

---

## Performance Optimization

### Processing Speed

| Signal | Typical Speed (CPU) | GPU Speedup |
|--------|-------------------|-------------|
| RPPG | ~5 FPS | Minimal |
| I3D | ~3 FPS | 5-10x |
| LipSync | ~8 FPS | Minimal |

### Tips for Faster Processing

1. **Use GPU** (especially for I3D)
2. **Sample frames** for very long videos
3. **Reduce resolution** if quality allows
4. **Process in parallel** (ensemble runs signals sequentially by default)

---

## Example Scripts

See the `examples/` directory:
- [`video_detection_example.py`](https://github.com/ADITYAMAHAKALI/veridex/blob/main/examples/video_detection_example.py) - Individual signals
- [`video_ensemble_example.py`](https://github.com/ADITYAMAHAKALI/veridex/blob/main/examples/video_ensemble_example.py) - Ensemble detection

---

## Research & Technical Details

### rPPG Method
Based on PhysNet architecture (Yu et al., 2019). Analyzes subtle color variations in facial skin to extract heartbeat patterns.

### I3D Method
Inception-3D (Carreira & Zisserman, 2017) trained on Kinetics-400 for action recognition, adapted for deepfake detection.

### LipSync Method
SyncNet (Chung & Zisserman, 2016) architecture for audio-visual correspondence.

**Full references**: See [Research Documentation](https://github.com/ADITYAMAHAKALI/veridex/blob/main/project_notes/research.md)

---

## Next Steps

1. **Obtain and integrate real model weights**
2. **Run on FaceForensics++ or Celeb-DF benchmarks**
3. **Calibrate confidence thresholds**
4. **Add real-time streaming support**

---

**Questions?** See [GitHub Issues](https://github.com/ADITYAMAHAKALI/veridex/issues) or [Contributing Guide](../CONTRIBUTING.md)
