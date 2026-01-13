# Testing Guide for Veridex Metrics

This guide explains how to test all metrics in the veridex package.

## Quick Start

Run the comprehensive test runner:

```bash
# Interactive mode - choose which dependencies to install
python3 run_all_tests.py
```

## Manual Testing by Module

### 1. Install Dependencies

Install all dependencies:
```bash
pip install -e ".[text,image,audio,dev]"
```

Or install specific modules:
```bash
# Text only
pip install -e ".[text,dev]"

# Audio only
pip install -e ".[audio,dev]"

# Image only
pip install -e ".[image,dev]"
```

### 2. Run Tests

Run all tests:
```bash
pytest tests/ -v
```

Run specific module tests:
```bash
# Text metrics
pytest tests/test_text_signals.py -v

# Image metrics
pytest tests/test_image_signals.py -v

# Audio metrics
pytest tests/audio/ -v

# New metrics
pytest tests/test_new_metrics.py -v
```

### 3. Run with Coverage

```bash
# All tests with coverage
pytest tests/ --cov=veridex --cov-report=html

# Specific module
pytest tests/audio/ --cov=veridex.audio --cov-report=term
```

## Available Metrics & Tests

### Text Metrics
- ✅ **ZlibEntropySignal** - Compression-based entropy
- ✅ **StylometricSignal** - Linguistic feature analysis
- ✅ **PerplexitySignal** - Perplexity and burstiness
- ✅ **BinocularsSignal** - Contrastive perplexity (requires models)

### Image Metrics
- ✅ **FrequencySignal** - Spectral analysis
- ✅ **ELASignal** - Error Level Analysis
- ✅ **DIRESignal** - Diffusion reconstruction error (requires diffusion models)

### Audio Metrics
- ✅ **SpectralSignal** - Frequency domain analysis
- ✅ **SilenceSignal** - Pause pattern detection
- ✅ **Wav2VecSignal** - Foundation model detection (requires pre-trained models)
- ✅ **AASISTSignal** - Spectro-temporal features

## Test Categories

### Unit Tests
Test individual signal implementations with mocked dependencies:
```bash
pytest tests/ -m "not integration"
```

### Integration Tests
Test with real models (slower, requires downloads):
```bash
pytest tests/ -m "integration"
```

### Dependency-Specific Tests
Tests automatically skip if dependencies are missing:
```bash
# Run only tests that don't require heavy dependencies
pytest tests/ --ignore=tests/audio/test_wav2vec*.py
```

## Troubleshooting

### Missing Dependencies
If tests fail due to missing dependencies:
1. Check which extras you installed
2. Install missing extras: `pip install -e ".[audio,text,image]"`

### Model Download Issues
Some tests require downloading models:
- **Wav2Vec**: ~1.2GB
- **Perplexity (GPT-2)**: ~500MB
- **Diffusion models**: Variable size

Set cache directory:
```bash
export HF_HOME=/path/to/cache
pytest tests/
```

### Memory Issues
Some tests require significant memory:
- Use `--maxfail=1` to stop after first failure
- Run modules separately
- Use smaller batch sizes

## CI/CD Testing

For continuous integration, use the minimal test set:
```bash
# Fast tests only (no model downloads)
pytest tests/ -v \
  --ignore=tests/audio/test_wav2vec_detector.py \
  -k "not slow"
```

## Example Output

```
================================ test session starts =================================
tests/test_text_signals.py::TestTextSignals::test_zlib_entropy PASSED        [ 16%]
tests/test_text_signals.py::TestTextSignals::test_perplexity_missing_deps PASSED [ 33%]
tests/audio/test_spectral.py::TestSpectralSignal::test_initialization PASSED [ 50%]
tests/audio/test_utils.py::TestAudioUtils::test_validate_audio PASSED        [ 66%]

============================== 6 passed in 2.34s ==================================
```

## Next Steps

After tests pass:
1. Review test coverage: `open htmlcov/index.html`
2. Try example scripts: `python examples/audio_detection_example.py`
3. Integrate into your application
