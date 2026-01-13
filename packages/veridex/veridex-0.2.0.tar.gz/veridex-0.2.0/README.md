# Veridex

<div align="center">
  <img src="https://raw.githubusercontent.com/ADITYAMAHAKALI/veridex/main/docs/images/veridex_logo.png" alt="Veridex Logo" width="200"/>
</div>

**A modular, probabilistic, and research-grounded AI content detection library.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ADITYAMAHAKALI/veridex/blob/main/LICENSE)
[![PyPI version](https://img.shields.io/badge/pypi-veridex-blue)](https://pypi.org/project/veridex/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/veridex?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/veridex)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://adityamahakali.github.io/veridex/)

Veridex is a production-ready library for detecting AI-generated content across multiple modalities: **text**, **image**, and **audio**. Unlike binary classifiers, Veridex provides probabilistic detection with confidence estimates and interpretable signals.

---

## 📑 Quick Navigation

| Section | Description |
|---------|-------------|
| [✨ Features](#-features) | Key capabilities of Veridex |
| [🚀 Quick Start](#-quick-start) | Installation and basic usage |
| [📦 Available Detectors](#-available-detectors) | Complete detector comparison |
| [🏗️ Architecture](#️-architecture) | System design and philosophy |
| [📚 Documentation](#-documentation) | Guides, tutorials, and API reference |
| [🧪 Testing](#-testing) | Running tests and coverage |
| [🤝 Contributing](#-contributing) | How to contribute |
| [🔬 Research](#-research--citations) | Academic papers and citations |
| [⚠️ Limitations](#️-limitations) | Important usage constraints |

---

## ✨ Features

- 🎯 **Multi-Modal Detection**: Text, Image, and Audio deepfake detection
- 📊 **Probabilistic Outputs**: Returns probabilities and confidence scores, not just binary labels
- 🔍 **Interpretable Signals**: Exposes individual detection features for transparency
- 🧩 **Modular Architecture**: Easy to extend with new detection methods
- 🚀 **Production-Ready**: Robust error handling, graceful degradation
- 📖 **Research-Grounded**: Based on state-of-the-art papers and benchmarks

## 💡 Use Cases

- **🛡️ Content Moderation**: Automatically flag AI-generated spam, fake profiles, and synthetic media.
- **🎓 Academic Integrity**: Verify the authenticity of student essays and research papers.
- **📰 Journalism & Media**: Validate sources and detect deepfake imagery in news gathering.
- **🎨 Copyright Protection**: Distinguish between human-created art and generative AI outputs.

## 🚀 Quick Start

### Installation

```bash
# Install core library
pip install veridex

# Install with specific modality support
pip install veridex[text]      # Text detection
pip install veridex[audio]     # Audio detection
pip install veridex[image]     # Image detection
pip install veridex[video]     # Video detection

# Install everything
pip install veridex[text,image,audio,video]

# Development installation
pip install -e ".[dev]"
```

### Usage Examples

#### Text Detection

```python
from veridex.text import PerplexitySignal, BinocularsSignal

# Quick detection with perplexity
detector = PerplexitySignal()
result = detector.run("This text seems suspiciously perfect...")

print(f"AI Probability: {result.score:.2f}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Perplexity: {result.metadata['mean_perplexity']:.2f}")
```

#### Audio Detection

```python
from veridex.audio import SpectralSignal

# Lightweight frequency analysis
detector = SpectralSignal()
result = detector.run("audio_sample.wav")

print(f"AI Probability: {result.score:.2f}")
print(f"Spectral Features: {result.metadata}")
```

#### Image Detection

```python
from veridex.image import FrequencySignal

# Analyze spectral anomalies
detector = FrequencySignal()
result = detector.run("suspicious_image.png")

print(f"AI Probability: {result.score:.2f}")
```

#### Video Detection

```python
from veridex.video import VideoEnsemble

# Combine multiple video signals (recommended)
ensemble = VideoEnsemble()
result = ensemble.run("video.mp4")

print(f"AI Probability: {result.score:.2f}")
print(f"Confidence: {result.confidence:.2f}")

# View individual signal contributions
for sig, res in result.metadata['individual_results'].items():
    print(f"{sig}: {res['score']:.2f}")
```

**👉 [See more examples in the examples/ directory](https://github.com/ADITYAMAHAKALI/veridex/tree/main/examples)**

---

## 📦 Available Detectors

### Text Detectors

| Detector | Method | Speed | Accuracy | GPU Required | Use Case |
|----------|--------|-------|----------|--------------|----------|
| `ZlibEntropySignal` | Compression-based | ⚡ Fast | ⭐ Low | ❌ No | Quick first-pass screening |
| `PerplexitySignal` | Statistical (LLM-based) | 🔄 Medium | ⭐⭐ Medium | 🔶 Optional | General-purpose detection |
| `BinocularsSignal` | Contrastive Perplexity | 🔄 Medium | ⭐⭐⭐ High | 🔶 Optional | High-accuracy text analysis |
| `StylometricSignal` | Linguistic Analysis | ⚡ Fast | ⭐ Low | ❌ No | Style pattern detection |

### Audio Detectors

| Detector | Method | Speed | Accuracy | GPU Required | Use Case |
|----------|--------|-------|----------|--------------|----------|
| `SpectralSignal` | Frequency Domain | ⚡ Fast | ⭐⭐ Medium | ❌ No | Lightweight audio screening |
| `AASISTSignal` | Spectro-Temporal | 🔄 Medium | ⭐⭐⭐ High | ❌ No | Anti-spoofing detection |
| `Wav2VecSignal` | Foundation Model | 🐌 Slow | ⭐⭐⭐⭐ Very High | ✅ Recommended | Production-grade detection |
| `SilenceSignal` | Pause Analysis | ⚡ Fast | ⭐ Low | ❌ No | Synthetic speech patterns |

### Image Detectors

| Detector | Method | Speed | Accuracy | GPU Required | Use Case |
|----------|--------|-------|---------|--------------| ---------|
| `FrequencySignal` | Spectral Analysis | ⚡ Fast | ⭐⭐ Medium | ❌ No | Quick image screening |
| `DIRESignal` | Diffusion Reconstruction | 🐌 Slow | ⭐⭐⭐ High | ✅ Yes | High-accuracy AI image detection |
| `ELASignal` | Error Level Analysis | ⚡ Fast | ⭐⭐ Medium | ❌ No | Image manipulation detection |

### Video Detectors

| Detector | Method | Speed | Accuracy | GPU Required | Use Case |
|----------|--------|-------|----------|--------------|----------|
| `RPPGSignal` | Biological (Heartbeat) | 🔄 Medium | ⭐⭐⭐ High | ❌ No | Face-swap deepfakes |
| `I3DSignal` | Spatiotemporal Motion | 🔄 Medium | ⭐⭐⭐ High | 🔶 Recommended | General video deepfakes |
| `LipSyncSignal` | Audio-Visual Sync | 🔄 Medium | ⭐⭐⭐ High | ❌ No | Dubbing/voice cloning |
| `VideoEnsemble` | Combines All Three | 🔄 Medium | ⭐⭐⭐⭐ Very High | 🔶 Recommended | **Production use** |

> **📺 Recommended**: Use `VideoEnsemble` for robust detection. Combines RPPG, I3D, and LipSync with confidence-weighted fusion.
> 
> **📖 [Video Detection Guide](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/tutorials/video_detection.md)** - Comprehensive documentation


**💡 See [Choosing the Right Detector](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/concepts/index.md) for guidance**

---

## 🏗️ Architecture

Veridex follows a signal-based architecture:

```
Input → Signal Extractors → Normalization → Fusion → Output
                ↓
    (Independent, Inspectable Signals)
```

Each detector:
- Inherits from `BaseSignal`
- Returns standardized `DetectionResult`
- Operates independently
- Declares its limitations explicitly

**Learn more:** [Architecture Documentation](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/concepts/index.md)

---

## 📚 Documentation

### 📖 Guides & Tutorials
- **[Getting Started Guide](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/getting_started.md)** - Installation and first steps
- **[Text Detection Tutorial](https://github.com/ADITYAMAHAKALI/veridex/blob/main/examples/text_detection_example.py)** - Step-by-step text analysis
- **[Image Detection Tutorial](https://github.com/ADITYAMAHAKALI/veridex/blob/main/examples/image_detection_example.py)** - Image deepfake detection
- **[Audio Detection Tutorial](https://github.com/ADITYAMAHAKALI/veridex/blob/main/examples/audio_detection_example.py)** - Voice deepfake detection
- **[Examples Directory](https://github.com/ADITYAMAHAKALI/veridex/tree/main/examples)** - Comprehensive examples

### 🔍 Concepts
- **[Core Concepts](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/concepts/index.md)** - Signal-based architecture
- **[Text Signals](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/concepts/text.md)** - Understanding text detection
- **[Image Signals](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/concepts/image.md)** - Understanding image detection
- **[Audio Signals](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/concepts/audio.md)** - Understanding audio detection

### 📘 API Reference
- **[Core API](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/api/core.md)** - BaseSignal, DetectionResult
- **[Text API](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/api/text.md)** - Text detectors
- **[Image API](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/api/image.md)** - Image detectors
- **[Audio API](https://github.com/ADITYAMAHAKALI/veridex/blob/main/docs/api/audio.md)** - Audio detectors

### 🔬 Technical Documentation
- **[Design Philosophy](https://github.com/ADITYAMAHAKALI/veridex/blob/main/project_notes/plan.md)** - System design and architecture
- **[Research Document](https://github.com/ADITYAMAHAKALI/veridex/blob/main/project_notes/research.md)** - Comprehensive technical analysis
- **[Testing Guide](https://github.com/ADITYAMAHAKALI/veridex/blob/main/TESTING.md)** - How to test all metrics
- **[Contributing Guide](https://github.com/ADITYAMAHAKALI/veridex/blob/main/CONTRIBUTING.md)** - Development guidelines

---

## 🧪 Testing

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev,text,audio,image]"

# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/audio/ -v

# With coverage
pytest tests/ --cov=veridex --cov-report=html
```

**See [TESTING.md](https://github.com/ADITYAMAHAKALI/veridex/blob/main/TESTING.md) for detailed testing guide.**

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/ADITYAMAHAKALI/veridex/blob/main/CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/ADITYAMAHAKALI/veridex.git
cd veridex

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode with all dependencies
pip install -e ".[dev,text,image,audio]"

# Run tests
pytest tests/

# Format code
black veridex/ tests/
flake8 veridex/
```

---

## 📄 License

Apache License 2.0 - See [LICENSE](https://github.com/ADITYAMAHAKALI/veridex/blob/main/LICENSE) for details.

---

## 🔬 Research & Citations

Veridex is based on cutting-edge research in AI-generated content detection. Key methods include:

- **Binoculars**: Spotting LLMs With Binoculars (arXiv:2401.12070)
- **AASIST**: Audio Anti-Spoofing Integrated Spectro-Temporal Graph Attention
- **DIRE**: Diffusion Reconstruction Error for deepfake images
- **Wav2Vec 2.0**: Self-supervised foundation models for audio

**See [Research Documentation](https://github.com/ADITYAMAHAKALI/veridex/blob/main/project_notes/research.md) for full references.**

---

## ⚠️ Limitations

Veridex is a **probabilistic detection tool**, not a definitive proof system:

- ❌ Not suitable as sole evidence for legal/forensic purposes
- ❌ Cannot detect all AI-generated content with 100% accuracy
- ❌ Vulnerable to adversarial attacks and post-processing
- ⚠️ Requires regular updates as generative models improve

**Always use multiple signals and human judgment for critical decisions.**

---

## 🗺️ Roadmap

- [x] Text detection (Perplexity, Binoculars)
- [x] Image detection (Frequency, DIRE)
- [x] Audio detection (Spectral, AASIST, Wav2Vec)
- [x] Video detection (rPPG, I3D, LipSync)
- [ ] C2PA provenance integration
- [ ] Ensemble fusion models
- [ ] Real-time streaming detection
- [ ] Model calibration on benchmarks

---

## 📧 Contact

For questions, issues, or contributions:
- **Email**: adityamahakali@aisolve.org
- **Issues**: [GitHub Issues](https://github.com/ADITYAMAHAKALI/veridex/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ADITYAMAHAKALI/veridex/discussions)
- **Contributing**: [CONTRIBUTING.md](https://github.com/ADITYAMAHAKALI/veridex/blob/main/CONTRIBUTING.md)

---

## 🌟 Star History

If you find Veridex useful, please consider giving it a ⭐ on GitHub!

---

**Built with ❤️ for transparency in the age of generative AI**
