# Frequently Asked Questions (FAQ)

Common questions about Veridex and AI content detection.

---

## General Questions

### What is Veridex?

Veridex is a Python library for detecting AI-generated content across text, images, and audio. Unlike binary classifiers, it provides probabilistic scores with confidence estimates and interpretable signals.

### How accurate is Veridex?

Accuracy varies by detector and modality:

- **Text**: 70-90% depending on detector (BinocularsSignal highest)
- **Image**: 75-92% (DIRESignal highest for diffusion models)
- **Audio**: 80-95% (Wav2VecSignal highest)

!!! warning "Important"
    No AI detector is 100% accurate. Always use multiple signals and human judgment for critical decisions.

### Can Veridex prove content is AI-generated?

**No.** Veridex provides probabilistic estimates, not definitive proof. It should not be used as sole evidence for:
- Legal proceedings
- Academic misconduct cases
- Content moderation decisions

Always combine with other evidence and human review.

### Is Veridex free to use?

Yes! Veridex is open-source under the Apache 2.0 license. You can:
- ✓ Use commercially
- ✓ Modify the code
- ✓ Distribute copies
- ✓ Use privately

See [LICENSE](https://github.com/ADITYAMAHAKALI/veridex/blob/main/LICENSE) for details.

---

## Installation & Setup

### What Python version do I need?

Python 3.9 or higher is required.

```bash
python --version  # Should be 3.9+
```

### Which installation should I use?

Choose based on your needs:

```bash
# All modalities (recommended for evaluation)
pip install veridex[text,image,audio]

# Specific modality (production)
pip install veridex[text]      # Text only
pip install veridex[image]     # Image only
pip install veridex[audio]     # Audio only

# Core only (minimal dependencies)
pip install veridex
```

### How large are the model downloads?

| Detector | Model Size | First-Run Download |
|----------|------------|-------------------|
| `PerplexitySignal` | ~500MB | GPT-2 |
| `BinocularsSignal` | ~7GB | GPT-2 + Falcon |
| `Wav2VecSignal` | ~1.2GB | Wav2Vec 2.0 |
| `DIRESignal` | ~4GB | Stable Diffusion |
| Others | None | No download |

Models are cached after first download.

### Can I use a custom cache directory?

Yes! Set environment variables:

```bash
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

---

## Usage Questions

### What's the difference between score and confidence?

- **Score (0.0-1.0)**: Probability that content is AI-generated
- **Confidence (0.0-1.0)**: How certain the detector is about the score

**Example**:
```python
result.score = 0.8       # 80% probability of AI
result.confidence = 0.9  # Very confident in this assessment
```

Low confidence means the detector is unsure → consider using additional signals.

### How do I choose which detector to use?

Use this decision matrix:

**Text**:
- Speed priority → `ZlibEntropySignal`
- Accuracy priority → `BinocularsSignal`
- Balanced → `PerplexitySignal`

**Image**:
- Quick screening → `FrequencySignal`
- High accuracy → `DIRESignal` (requires GPU)
- Manipulation detection → `ELASignal`

**Audio**:
- Lightweight → `SpectralSignal`
- Anti-spoofing → `AASISTSignal`
- Production-grade → `Wav2VecSignal`

### Can I combine multiple detectors?

Yes! This is recommended for better accuracy:

```python
from veridex.text import PerplexitySignal, ZlibEntropySignal

text = "Your text..."

# Run multiple detectors
detectors = [PerplexitySignal(), ZlibEntropySignal()]
scores = [d.run(text).score for d in detectors]

# Average the scores
ensemble_score = sum(scores) / len(scores)
```

See [Ensemble Detection Tutorial](tutorials/ensemble_detection.md) for advanced techniques.

### What input formats are supported?

=== "Text"
    - Plain text strings
    - Any encoding (UTF-8 recommended)
    - Min length: ~10 words for reliable results

=== "Image"
    - Formats: PNG, JPEG, WebP, TIFF
    - Any resolution (will be resized if needed)
    - RGB or grayscale

=== "Audio"
    - Formats: WAV, MP3, FLAC, OGG
    - Sample rates: Any (will be resampled to 16kHz)
    - Mono or stereo (converted to mono)

---

## Performance Questions

### Do I need a GPU?

**Optional** for most detectors:

| Detector | GPU Required | Speedup with GPU |
|----------|--------------|------------------|
| `PerplexitySignal` | No | 2-3x faster |
| `BinocularsSignal` | No | 2-3x faster |
| `DIRESignal` | **Yes** | 10-20x faster |
| `Wav2VecSignal` | No | 5-10x faster |
| Others | No | Minimal |

`DIRESignal` (image) strongly recommended to use GPU.

### How fast is Veridex?

Approximate processing times (CPU):

**Text** (1000 words):
- `ZlibEntropySignal`: <0.1s
- `PerplexitySignal`: 2-5s
- `BinocularsSignal`: 10-20s

**Image** (1024x1024):
- `FrequencySignal`: <1s
- `ELASignal`: <1s
- `DIRESignal`: 30-60s (GPU: 3-5s)

**Audio** (30 seconds):
- `SpectralSignal`: <1s
- `AASISTSignal`: 2-5s
- `Wav2VecSignal`: 10-20s

### Can I batch process files?

Yes! Just loop through your files:

```python
from veridex.text import PerplexitySignal

detector = PerplexitySignal()

texts = ["text1...", "text2...", "text3..."]
results = [detector.run(text) for text in texts]
```

For production, consider using async processing or multiprocessing.

---

## Technical Questions

### What ML frameworks does Veridex use?

- **PyTorch** (via transformers) for LLM-based detectors
- **NumPy/SciPy** for signal processing
- **librosa** for audio analysis
- **PIL/OpenCV** for image processing

### Can I fine-tune the detectors?

Not currently. Detectors use pre-trained models. Future versions may support custom training.

### Can I add my own detectors?

Yes! Extend the `BaseSignal` class:

```python
from veridex.core import BaseSignal, DetectionResult

class MyCustomSignal(BaseSignal):
    def run(self, input_data):
        # Your detection logic here
        score = 0.5  # Calculate score
        confidence = 0.8
        metadata = {"custom_metric": 123}
        
        return DetectionResult(
            score=score,
            confidence=confidence,
            metadata=metadata
        )
```

See [API Reference](api/core.md) for details.

### Does Veridex send data to external servers?

**No.** All processing happens locally. Models are downloaded fromHugging Face on first use and cached locally.

---

## Limitations & Edge Cases

### Can Veridex detect all AI-generated content?

No. Veridex has limitations:

- ❌ Cannot detect all AI models (trained on common ones)
- ❌ Vulnerable to adversarial attacks
- ❌ Accuracy degrades with post-processing/editing
- ❌ Newer/unknown models may evade detection

### What about paraphrased AI content?

Detectors vary in robustness:
- `BinocularsSignal`: More robust to paraphrasing
- `PerplexitySignal`: Moderately robust
- `ZlibEntropySignal`: Less robust

Heavily paraphrased content may evade detection.

### Can it detect AI-assisted (human-edited) content?

This is challenging. If a human significantly edits AI content, it becomes a hybrid that's hard to classify.

### What about content from new AI models?

Detectors may not recognize very new models (e.g., GPT-5, future models). Regular updates are needed.

---

## Error Messages

### "ImportError: No module named 'transformers'"

Install the required dependencies:

```bash
pip install veridex[text]  # For text detectors
pip install veridex[image]  # For image detectors
pip install veridex[audio]  # For audio detectors
```

### "Model download failed"

Check your internet connection and try:

```bash
# Set custom cache and retry
export HF_HOME=/tmp/hf_cache
python -c "from veridex.text import PerplexitySignal; PerplexitySignal()"
```

### "CUDA out of memory"

Reduce batch size or use CPU:

```python
import torch
torch.cuda.empty_cache()  # Free GPU memory

# Force CPU usage
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
```

---

## Getting Help

### Where can I get support?

- 📖 [Documentation](index.md)
- 🐛 [GitHub Issues](https://github.com/ADITYAMAHAKALI/veridex/issues) - Bug reports
- 💬 [GitHub Discussions](https://github.com/ADITYAMAHAKALI/veridex/discussions) - Questions
- 📧 [Email](mailto:adityamahakali@aisolve.org) - Direct contact

### How do I report a bug?

1. Check [existing issues](https://github.com/ADITYAMAHAKALI/veridex/issues)
2. Create a new issue with:
   - Veridex version (`pip show veridex`)
   - Python version
   - OS and system info
   - Minimal code to reproduce
   - Error message/traceback

### Can I contribute?

Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Additional Resources

- [Quick Start Tutorial](tutorials/quick_start.md)
- [Troubleshooting Guide](troubleshooting.md)
- [API Reference](api/core.md)
- [Research Papers](research/index.md)
