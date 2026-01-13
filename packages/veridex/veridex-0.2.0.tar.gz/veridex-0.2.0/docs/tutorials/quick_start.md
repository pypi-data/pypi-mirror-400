# Quick Start (5 Minutes)

Get up and running with Veridex in under 5 minutes!

---

## Step 1: Installation

Choose your installation based on what you want to detect:

=== "All Modalities"

    ```bash
    pip install veridex[text,image,audio]
    ```

=== "Text Only"

    ```bash
    pip install veridex[text]
    ```

=== "Image Only"

    ```bash
    pip install veridex[image]
    ```

=== "Audio Only"

    ```bash
    pip install veridex[audio]
    ```

=== "Core Only"

    ```bash
    # Lightweight, only numpy/scipy
    pip install veridex
    ```

!!! tip "Installation Time"
    Core library installs in seconds. Full installation with all dependencies may take 2-3 minutes.

---

## Step 2: Your First Detection

### Text Detection

Detect AI-generated text in 3 lines of code:

```python
from veridex.text import PerplexitySignal

detector = PerplexitySignal()
result = detector.run("The artificial intelligence landscape has evolved dramatically.")

print(f"AI Probability: {result.score:.2%}")
print(f"Confidence: {result.confidence:.2%}")
```

**Output:**
```
AI Probability: 78%
Confidence: 65%
```

### Image Detection

Detect AI-generated images:

```python
from veridex.image import FrequencySignal

detector = FrequencySignal()
result = detector.run("path/to/image.png")

print(f"AI Probability: {result.score:.2%}")
print(f"Confidence: {result.confidence:.2%}")
```

### Audio Detection

Detect synthetic voice:

```python
from veridex.audio import SpectralSignal

detector = SpectralSignal()
result = detector.run("path/to/audio.wav")

print(f"AI Probability: {result.score:.2%}")
print(f"Confidence: {result.confidence:.2%}")
```

---

## Step 3: Understanding Results

Every detector returns a `DetectionResult` with:

```python
result = detector.run(input_data)

# Core fields
result.score        # 0.0-1.0: Probability of AI-generated content
result.confidence   # 0.0-1.0: How confident the detector is
result.metadata     # Dict with additional metrics
```

### Interpreting Scores

| Score Range | Interpretation |
|-------------|----------------|
| 0.0 - 0.3 | Likely human-generated |
| 0.3 - 0.7 | Uncertain (use additional signals) |
| 0.7 - 1.0 | Likely AI-generated |

!!! warning "Important"
    - **Score** ≠ certainty! Always check **confidence**
    - Low confidence means the detector is unsure
    - Combine multiple signals for better accuracy

---

## Step 4: Exploring Metadata

Each detector provides modality-specific metadata:

=== "Text"

    ```python
    from veridex.text import PerplexitySignal
    
    detector = PerplexitySignal()
    result = detector.run("Your text here...")
    
    # Access metadata
    print(f"Mean Perplexity: {result.metadata['mean_perplexity']:.2f}")
    print(f"Burstiness: {result.metadata.get('burstiness', 'N/A')}")
    ```

=== "Image"

    ```python
    from veridex.image import FrequencySignal
    
    detector = FrequencySignal()
    result = detector.run("image.png")
    
    # Access metadata
    print(f"High Freq Score: {result.metadata.get('high_freq_score', 'N/A')}")
    ```

=== "Audio"

    ```python
    from veridex.audio import SpectralSignal
    
    detector = SpectralSignal()
    result = detector.run("audio.wav")
    
    # Access metadata
    print(f"High Freq Energy: {result.metadata.get('high_freq_energy', 'N/A')}")
    print(f"Spectral Rolloff: {result.metadata.get('spectral_rolloff', 'N/A')}")
    ```

---

## Step 5: Try Multiple Detectors

Each modality has multiple detectors. Try them all!

### Text Detectors

```python
from veridex.text import (
    PerplexitySignal,      # Statistical analysis
    BinocularsSignal,      # High accuracy (slower)
    ZlibEntropySignal,     # Fast compression-based
    StylometricSignal      # Linguistic patterns
)

text = "Your text here..."

# Compare results
for DetectorClass in [PerplexitySignal, ZlibEntropySignal, StylometricSignal]:
    detector = DetectorClass()
    result = detector.run(text)
    print(f"{detector.__class__.__name__}: {result.score:.2%}")
```

### Image Detectors

```python
from veridex.image import (
    FrequencySignal,  # Fast spectral analysis
    ELASignal,              # Error level analysis
    # DIRESignal,           # High accuracy (requires GPU)
)

image_path = "image.png"

for DetectorClass in [FrequencySignal, ELASignal]:
    detector = DetectorClass()
    result = detector.run(image_path)
    print(f"{detector.__class__.__name__}: {result.score:.2%}")
```

### Audio Detectors

```python
from veridex.audio import (
    SpectralSignal,    # Fast frequency analysis
    SilenceSignal,     # Pause pattern detection
    # AASISTSignal,    # Spectro-temporal (slower)
    # Wav2VecSignal,   # Foundation model (slowest, most accurate)
)

audio_path = "audio.wav"

for DetectorClass in [SpectralSignal, SilenceSignal]:
    detector = DetectorClass()
    result = detector.run(audio_path)
    print(f"{detector.__class__.__name__}: {result.score:.2%}")
```

---

## Common Issues

### ImportError: No module named 'transformers'

You need to install the modality-specific dependencies:

```bash
pip install veridex[text]  # For text detection
```

### Model Download Slow

Some detectors download models on first use:
- `PerplexitySignal`: ~500MB (GPT-2)
- `BinocularsSignal`: ~7GB (GPT-2 + Falcon)
- `Wav2VecSignal`: ~1.2GB

Set a custom cache directory:

```bash
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

### GPU Not Detected

For GPU support (optional for most detectors):

```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## What's Next?

Congratulations! You've completed the quick start. 🎉

### Next Steps

<div class="next-steps">
  <ol>
    <li><a href="text_detection_guide/">Text Detection Guide</a> - Deep dive into text analysis</li>
    <li><a href="image_detection_guide/">Image Detection Guide</a> - Master image deepfake detection</li>
    <li><a href="audio_detection_guide/">Audio Detection Guide</a> - Detect voice deepfakes</li>
    <li><a href="ensemble_detection/">Ensemble Detection</a> - Combine multiple signals</li>
  </ol>
</div>

### Additional Resources

- [Concepts](../concepts/index.md) - Understand the architecture
- [API Reference](../api/core.md) - Complete API documentation
- [Examples](https://github.com/ADITYAMAHAKALI/veridex/tree/main/examples) - More code examples
- [FAQ](../faq.md) - Common questions

---

## Need Help?

- 📖 [Documentation](../index.md)
- ❓ [FAQ](../faq.md)
- 🐛 [GitHub Issues](https://github.com/ADITYAMAHAKALI/veridex/issues)
- 💬 [Discussions](https://github.com/ADITYAMAHAKALI/veridex/discussions)
