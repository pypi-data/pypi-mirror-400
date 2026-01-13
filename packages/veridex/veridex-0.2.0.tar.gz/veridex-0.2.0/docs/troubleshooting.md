# Troubleshooting Guide

Solutions to common issues when using Veridex.

---

## Installation Issues

### Problem: `pip install veridex` fails

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement veridex
```

**Solutions**:

1. **Update pip**:
   ```bash
   pip install --upgrade pip
   ```

2. **Check Python version** (requires 3.9+):
   ```bash
   python --version
   ```

3. **Try with specific index**:
   ```bash
   pip install --index-url https://pypi.org/simple/ veridex
   ```

---

### Problem: Dependency conflicts

**Symptoms**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Solutions**:

1. **Use a fresh virtual environment**:
   ```bash
   python -m venv fresh_venv
   source fresh_venv/bin/activate  # On Windows: fresh_venv\Scripts\activate
   pip install veridex[text,image,audio]
   ```

2. **Install with --no-deps and then dependencies**:
   ```bash
   pip install --no-deps veridex
   pip install -r requirements.txt
   ```

3. **Use conda environment**:
   ```bash
   conda create -n veridex python=3.10
   conda activate veridex
   pip install veridex[text,image,audio]
   ```

---

## Import Errors

### Problem: "No module named 'transformers'"

**Symptoms**:
```python
ImportError: No module named 'transformers'
```

**Solution**:

Install the appropriate extras:

```bash
# For text detectors
pip install veridex[text]

# For all modalities
pip install veridex[text,image,audio]
```

**Verification**:
```bash
pip list | grep transformers
```

---

### Problem: "No module named 'librosa'"

**Symptoms**:
```python
ImportError: No module named 'librosa'
```

**Solution**:

Install audio dependencies:

```bash
pip install veridex[audio]
```

---

### Problem: "No module named 'PIL'" or "No module named 'cv2'"

**Solution**:

Install image dependencies:

```bash
pip install veridex[image]

# Or manually:
pip install Pillow opencv-python
```

---

## Model Download Issues

### Problem: Model download is very slow

**Symptoms**:
- First run takes 10+ minutes
- Downloads seem stuck

**Solutions**:

1. **Check your internet connection**

2. **Set custom cache directory** (if disk space limited):
   ```bash
   export HF_HOME=/path/with/more/space
   python your_script.py
   ```

3. **Use a mirror** (in some regions):
   ```python
   import os
   os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
   ```

4. **Pre-download models**:
   ```python
   from transformers import AutoModel, AutoTokenizer
   
   # Download GPT-2 beforehand
   AutoTokenizer.from_pretrained("gpt2")
   AutoModel.from_pretrained("gpt2")
   ```

---

### Problem: "HTTPError: 404 Client Error"

**Symptoms**:
```
HTTPError: 404 Client Error: Not Found for url
```

**Solution**:

This usually means the model name is incorrect or you're offline.

1. **Check model name** in detector initialization
2. **Verify internet connection**
3. **Try with explicit model_id**:
   ```python
   from veridex.text import PerplexitySignal
   detector = PerplexitySignal(model_id="gpt2")  # Explicit model
   ```

---

## Runtime Errors

### Problem: "CUDA out of memory"

**Symptoms**:
```
RuntimeError: CUDA out of memory. Tried to allocate X MiB (GPU 0; Y GiB total capacity)
```

**Solutions**:

1. **Force CPU usage**:
   ```python
   import os
   os.environ["CUDA_VISIBLE_DEVICES"] = ""
   
   from veridex.text import PerplexitySignal
   detector = PerplexitySignal()
   ```

2. **Clear GPU cache**:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

3. **Use smaller model**:
   ```python
   # Use DistilGPT-2 instead of GPT-2
   detector = PerplexitySignal(model_id="distilgpt2")
   ```

4. **Process in smaller batches**

---

### Problem: "TypeError: run() missing required argument"

**Symptoms**:
```python
TypeError: run() missing 1 required positional argument: 'input_data'
```

**Solution**:

Make sure you're calling `run()` with the input data:

```python
# ❌ Wrong
detector = PerplexitySignal()
result = detector.run()  # Missing input!

# ✓ Correct
detector = PerplexitySignal()
result = detector.run("Your text here")  # Provide input
```

---

### Problem: "ValueError: Text too short"

**Symptoms**:
```
ValueError: Input text must be at least 10 tokens
```

**Solution**:

Provide longer text (at least 10 words):

```python
# ❌ Too short
result = detector.run("Hi")  

# ✓ Better
result = detector.run("This is a longer text that provides enough context for analysis.")
```

---

### Problem: Audio file not loading

**Symptoms**:
```
Error: Could not load audio file
```

**Solutions**:

1. **Check file format** (WAV, MP3, FLAC supported):
   ```python
   import librosa
   # Test if file is readable
   audio, sr = librosa.load("audio.wav")
   print(f"Loaded: {len(audio)} samples at {sr} Hz")
   ```

2. **Install ffmpeg** (for MP3 support):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/
   ```

3. **Convert to WAV**:
   ```python
   from pydub import AudioSegment
   audio = AudioSegment.from_mp3("input.mp3")
   audio.export("output.wav", format="wav")
   ```

---

### Problem: Image file not loading

**Symptoms**:
```
PIL.UnidentifiedImageError: cannot identify image file
```

**Solutions**:

1. **Verify image format**:
   ```python
   from PIL import Image
   try:
       img = Image.open("image.png")
       print(f"Format: {img.format}, Size: {img.size}")
   except Exception as e:
       print(f"Error: {e}")
   ```

2. **Convert image format**:
   ```python
   from PIL import Image
   img = Image.open("image.webp")
   img.save("image.png", "PNG")
   ```

3. **Check file path** - use absolute paths:
   ```python
   import os
   image_path = os.path.abspath("image.png")
   result = detector.run(image_path)
   ```

---

## Performance Issues

### Problem: Detection is very slow

**Symptoms**:
- Takes minutes to process
- CPU usage at 100%

**Solutions**:

1. **Use GPU if available**:
   ```python
   import torch
   print(f"CUDA available: {torch.cuda.is_available()}")
   
   # Install GPU-enabled PyTorch if needed
   # pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Use faster detectors**:
   ```python
   # ❌ Slow for quick checks
   from veridex.text import BinocularsSignal
   
   # ✓ Fast alternative
   from veridex.text import ZlibEntropySignal, PerplexitySignal
   ```

3. **Batch processing** (for multiple files):
   ```python
   detector = PerplexitySignal()
   
   # Reuse detector instance
   for text in texts:
       result = detector.run(text)  # Faster than creating new detector each time
   ```

---

### Problem: High memory usage

**Symptoms**:
- Python process using >4GB RAM
- System becoming slow

**Solutions**:

1. **Clear model cache after processing**:
   ```python
   import gc
   import torch
   
   result = detector.run(input_data)
   
   # Clear memory
   del detector
   gc.collect()
   if torch.cuda.is_available():
       torch.cuda.empty_cache()
   ```

2. **Process files one at a time**:
   ```python
   # ❌ Loads all in memory
   results = [detector.run(text) for text in large_text_list]
   
   # ✓ Process iteratively
   for text in large_text_list:
       result = detector.run(text)
       process_result(result)  # Handle immediately
   ```

---

## Platform-Specific Issues

### macOS: "library not loaded" error

**Symptoms**:
```
Library not loaded: @rpath/libsndfile.dylib
```

**Solution**:

Install libsndfile:
```bash
brew install libsndfile
```

---

### Windows: "DLL load failed"

**Symptoms**:
```
ImportError: DLL load failed while importing _imaging
```

**Solutions**:

1. **Install Visual C++ Redistributable**:
   - Download from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

2. **Reinstall Pillow**:
   ```bash
   pip uninstall Pillow
   pip install --no-cache-dir Pillow
   ```

---

### Linux: Missing system libraries

**Symptoms**:
```
OSError: libsndfile.so.1: cannot open shared object file
```

**Solution**:

Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    libsndfile1 \
    ffmpeg \
    libavcodec-extra \
    python3-dev

# CentOS/RHEL
sudo yum install -y libsndfile ffmpeg python3-devel
```

---

## Results Interpretation Issues

### Problem: Confidence is always low

**Symptoms**:
- `result.confidence < 0.5` for all inputs

**Explanation**:

Low confidence means the detector is genuinely uncertain. This can happen when:
- Input is ambiguous
- Input is at the boundary between AI/human
- Detector is not well-suited for this type of content

**Solutions**:

1. **Try a different detector**
2. **Use ensemble approach** (multiple detectors)
3. **Check input quality** (is text too short? Image too small?)

---

### Problem: Inconsistent results

**Symptoms**:
- Same input gives different scores on different runs

**Explanation**:

Some detectors have non-deterministic components (e.g., model inference with dropout).

**Solution**:

Set random seed for reproducibility:

```python
import torch
import numpy as np
import random

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(42)
result = detector.run(input_data)
```

---

## Getting More Help

If your issue isn't covered here:

1. **Check the [FAQ](faq.md)**
2. **Search [GitHub Issues](https://github.com/ADITYAMAHAKALI/veridex/issues)**
3. **Ask in [GitHub Discussions](https://github.com/ADITYAMAHAKALI/veridex/discussions)**
4. **Open a new issue** with:
   - Veridex version: `pip show veridex`
   - Python version: `python --version`
   - OS: `uname -a` (Linux/macOS) or `ver` (Windows)
   - Full error message and traceback
   - Minimal code to reproduce

---

## Useful Debugging Commands

```bash
# Check installed version
pip show veridex

# List all dependencies
pip list | grep -E "veridex|transformers|torch|librosa|PIL"

# Check Python version
python --version

# Check CUDA availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Test basic import
python -c "from veridex.core import BaseSignal; print('OK')"

# Check disk space for model cache
df -h $HOME/.cache/huggingface
```

---

## Additional Resources

- [FAQ](faq.md)
- [Quick Start](tutorials/quick_start.md)
- [API Reference](api/core.md)
- [GitHub Issues](https://github.com/ADITYAMAHAKALI/veridex/issues)
