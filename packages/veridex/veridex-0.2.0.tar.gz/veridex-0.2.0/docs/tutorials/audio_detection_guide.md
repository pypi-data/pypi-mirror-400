# Audio Detection Guide

Comprehensive guide to detecting synthetic voice and deepfake audio using Veridex.

---

## Overview

Veridex offers multiple audio detection signals, from lightweight spectral analysis to foundation model-based detection.

## Available Detectors

### 1. SpectralSignal (Fastest)

```python
from veridex.audio import SpectralSignal

detector = SpectralSignal()
result = detector.run("audio.wav")

print(f"AI Probability: {result.score:.2%}")
```

**Best for**: Quick screening, real-time applications

---

### 2. AASISTSignal (Anti-Spoofing)

```python
from veridex.audio import AASISTSignal

detector = AASISTSignal()
result = detector.run("audio.wav")

print(f"AI Probability: {result.score:.2%}")
```

**Best for**: Voice spoofing detection

---

### 3. Wav2VecSignal (Highest Accuracy)

```python
from veridex.audio import Wav2VecSignal

detector = Wav2VecSignal()
result = detector.run("audio.wav")

print(f"AI Probability: {result.score:.2%}")
```

**Best for**: Production-grade detection

---

### 4. SilenceSignal (Pattern Analysis)

```python
from veridex.audio import SilenceSignal

detector = SilenceSignal()
result = detector.run("audio.wav")

print(f"AI Probability: {result.score:.2%}")
```

**Best for**: Detecting synthetic speech patterns

---

## Best Practices

1. **Ensure proper audio format** (WAV recommended)
2. **Check sample rate** (16kHz optimal)
3. **Combine multiple signals**
4. **Consider computational resources**

---

## Next Steps

- [Ensemble Detection](ensemble_detection.md)
- [API Reference](../api/audio.md)
- [Performance Guide](../performance.md)
