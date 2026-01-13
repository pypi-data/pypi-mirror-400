# Image Detection Guide

Comprehensive guide to detecting AI-generated images using Veridex.

---

## Overview

Veridex provides multiple signals for detecting AI-generated images, from quick spectral analysis to sophisticated diffusion artifact detection.

## Available Detectors

### 1. FrequencySignal (Recommended for Quick Screening)

```python
from veridex.image import FrequencySignal

detector = FrequencySignal()
result = detector.run("image.png")

print(f"AI Probability: {result.score:.2%}")
```

**Best for**: Fast initial screening, batch processing

---

### 2. DIRESignal (Highest Accuracy)

```python
from veridex.image import DIRESignal

detector = DIRESignal()
result = detector.run("image.png")

print(f"AI Probability: {result.score:.2%}")
```

**Best for**: Production-grade detection, requires GPU

---

### 3. ELASignal (Manipulation Detection)

```python
from veridex.image import ELASignal

detector = ELASignal()
result = detector.run("image.png")

print(f"AI Probability: {result.score:.2%}")
```

**Best for**: Detecting image manipulation and editing

---

## Best Practices

1. **Preprocess images consistently**
2. **Use multiple detectors for important decisions**
3. **Consider GPU for DIRESignal**
4. **Check image format and size**

---

## Next Steps

- [Audio Detection Guide](audio_detection_guide.md)
- [Ensemble Detection](ensemble_detection.md)
- [API Reference](../api/image.md)
