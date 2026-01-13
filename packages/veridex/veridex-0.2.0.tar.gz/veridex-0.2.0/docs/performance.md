# Performance Optimization

Guide to optimizing Veridex for speed and resource efficiency.

---

## Performance Overview

Veridex performance varies by detector and hardware:

| Factor | Impact | Optimization |
|--------|--------|--------------|
| **GPU availability** | 2-20x speedup | Enable CUDA for compatible detectors |
| **Model size** | Affects load time & memory | Choose smaller models when possible |
| **Batch size** | Linear scaling | Process multiple items together |
| **Caching** | Faster subsequent runs | Reuse detector instances |

---

## Hardware Recommendations

### Minimum Requirements

- **CPU**: 2+ cores, 2.0+ GHz
- **RAM**: 4GB (8GB for image/audio)
- **Storage**: 10GB free (for model cache)
- **GPU**: Optional (CPU-only works)

### Recommended for Production

- **CPU**: 4+ cores, 3.0+ GHz (or equivalent)
- **RAM**: 16GB+
- **Storage**: 50GB free SSD
- **GPU**: NVIDIA GPU with 6GB+ VRAM (for DIRESignal, Wav2VecSignal)

---

## Detector Performance Comparison

### Text Detectors

| Detector | Speed (1000 words) | Memory | GPU Benefit |
|----------|-------------------|--------|-------------|
| `ZlibEntropySignal` | <0.1s | ~50MB | ❌ None |
| `StylometricSignal` | <0.1s | ~100MB | ❌ None |
| `PerplexitySignal` | 2-5s (CPU)<br>0.5-1s (GPU) | ~2GB | ✅ 3-5x |
| `BinocularsSignal` | 10-20s (CPU)<br>2-4s (GPU) | ~8GB | ✅ 4-6x |

### Image Detectors

| Detector | Speed (1024x1024) | Memory | GPU Benefit |
|----------|------------------|--------|-------------|
| `FrequencySignal` | <1s | ~200MB | ❌ Minimal |
| `ELASignal` | <1s | ~200MB | ❌ Minimal |
| `DIRESignal` | 30-60s (CPU)<br>3-5s (GPU) | ~5GB | ✅ 10-20x |

### Audio Detectors

| Detector | Speed (30s audio) | Memory | GPU Benefit |
|----------|------------------|--------|-------------|
| `SpectralSignal` | <1s | ~100MB | ❌ None |
| `SilenceSignal` | <1s | ~100MB | ❌ None |
| `AASISTSignal` | 2-5s | ~1GB | ✅ 2-3x |
| `Wav2VecSignal` | 10-20s (CPU)<br>2-4s (GPU) | ~3GB | ✅ 5-10x |

---

## Optimization Strategies

### 1. Choose the Right Detector

Use fast detectors for initial screening, expensive ones for confirmation:

```python
from veridex.text import ZlibEntropySignal, PerplexitySignal

def smart_text_detection(text):
    # Quick filter first
    quick_detector = ZlibEntropySignal()
    quick_result = quick_detector.run(text)
    
    # Only run expensive detector if needed
    if quick_result.score < 0.4:
        return quick_result  # Clearly human, skip expensive check
    
    # Run accurate detector
    accurate_detector = PerplexitySignal()
    return accurate_detector.run(text)
```

**Speedup**: 3-5x for mostly human content

---

### 2. Reuse Detector Instances

**❌ Slow** (creates new detector each time):
```python
for text in texts:
    detector = PerplexitySignal()  # Model loaded every time!
    result = detector.run(text)
```

**✅ Fast** (reuse detector):
```python
detector = PerplexitySignal()  # Load once
for text in texts:
    result = detector.run(text)  # Reuse
```

**Speedup**: 2-10x (avoids model reload)

---

### 3. Enable GPU Acceleration

Check if GPU is available:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

Install GPU-enabled PyTorch:

```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

Force GPU usage:

```python
from veridex.text import PerplexitySignal
import torch

# Ensure GPU is used
detector = PerplexitySignal()
# Models automatically use GPU if available
```

Force CPU (if needed):

```python
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable GPU
```

---

### 4. Batch Processing

For multiple items, process in batches:

```python
from veridex.text import PerplexitySignal

detector = PerplexitySignal()

# Process list of texts
texts = ["Text 1...", "Text 2...", "Text 3..."]

# ❌ One by one (slow)
results = [detector.run(text) for text in texts]

# ✅ Optimized with reused detector
detector = PerplexitySignal()
results = []
for text in texts:
    result = detector.run(text)
    results.append(result)
```

For parallel processing:

```python
from multiprocessing import Pool
from veridex.text import ZlibEntropySignal

def detect_text(text):
    detector = ZlibEntropySignal()  # Lightweight, ok to create
    return detector.run(text)

if __name__ == '__main__':
    texts = ["Text 1...", "Text 2...", ...]
    
    with Pool(processes=4) as pool:
        results = pool.map(detect_text, texts)
```

**Note**: Only use multiprocessing for lightweight detectors. GPU detectors may conflict.

---

### 5. Optimize Model Cache

Set custom cache location:

```bash
# Set in shell
export HF_HOME=/fast/ssd/hf_cache
export TRANSFORMERS_CACHE=/fast/ssd/hf_cache

# Or in Python
import os
os.environ['HF_HOME'] = '/fast/ssd/hf_cache'
```

Pre-download models:

```python
from transformers import AutoModel, AutoTokenizer

# Download during setup, not runtime
models = ["gpt2", "facebook/wav2vec2-base"]
for model_id in models:
    AutoTokenizer.from_pretrained(model_id)
    AutoModel.from_pretrained(model_id)
```

---

### 6. Reduce Model Size

Use smaller models for faster inference:

```python
# ❌ Large model (slow but accurate)
detector = PerplexitySignal(model_id="gpt2-large")

# ✅ Smaller model (faster, slightly less accurate)
detector = PerplexitySignal(model_id="distilgpt2")
```

Model size comparison:

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `distilgpt2` | ~350MB | Fast | Good |
| `gpt2` | ~500MB | Medium | Better |
| `gpt2-large` | ~3GB | Slow | Best |

---

### 7. Memory Management

Clear GPU cache:

```python
import torch
import gc

# After processing batch
results = process_batch(texts)

# Clear memory
torch.cuda.empty_cache()
gc.collect()
```

Limit memory usage:

```python
# Set max memory per GPU (in MB)
import torch
torch.cuda.set_per_process_memory_fraction(0.8)  # Use max 80% of GPU memory
```

---

## Production Deployment Patterns

### Pattern 1: Two-Stage Pipeline

```python
class TwoStageDetector:
    def __init__(self):
        self.stage1 = ZlibEntropySignal()  # Fast filter
        self.stage2 = PerplexitySignal()   # Accurate detector
    
    def detect(self, text):
        # Stage 1: Quick filter
        quick_result = self.stage1.run(text)
        
        if quick_result.score < 0.3:
            # Clearly human, skip stage 2
            return quick_result
        elif quick_result.score > 0.8:
            # Clearly AI, skip stage 2
            return quick_result
        else:
            # Uncertain, run stage 2
            return self.stage2.run(text)
```

**Benefit**: 50-70% reduction in expensive detector calls

---

### Pattern 2: Caching Results

```python
from functools import lru_cache
import hashlib

class CachedDetector:
    def __init__(self):
        self.detector = PerplexitySignal()
    
    def detect(self, text):
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return self._cached_detect(text_hash, text)
    
    @lru_cache(maxsize=1000)
    def _cached_detect(self, text_hash, text):
        return self.detector.run(text)
```

**Benefit**: Instant return for repeated content

---

### Pattern 3: Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncDetector:
    def __init__(self):
        self.detector = PerplexitySignal()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def detect_async(self, text):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.detector.run,
            text
        )
        return result
    
    async def detect_batch_async(self, texts):
        tasks = [self.detect_async(text) for text in texts]
        return await asyncio.gather(*tasks)

# Usage
async def main():
    detector = AsyncDetector()
    results = await detector.detect_batch_async(texts)

asyncio.run(main())
```

---

## Benchmarking

### Measure Your Performance

```python
import time

def benchmark_detector(detector, inputs, num_runs=10):
    times = []
    
    # Warmup
    detector.run(inputs[0])
    
    # Benchmark
    for _ in range(num_runs):
        start = time.time()
        for inp in inputs:
            detector.run(inp)
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    throughput = len(inputs) * num_runs / sum(times)
    
    print(f"Average time: {avg_time:.2f}s")
    print(f"Throughput: {throughput:.2f} items/s")
    print(f"Per-item: {avg_time/len(inputs)*1000:.2f}ms")

# Example
from veridex.text import PerplexitySignal

detector = PerplexitySignal()
texts = ["Sample text..." for _ in range(10)]
benchmark_detector(detector, texts)
```

---

## Cloud Deployment Recommendations

### AWS

```yaml
# Recommended EC2 instances
# CPU-only:
- Instance: c6i.xlarge
  vCPU: 4
  RAM: 8 GB
  Cost: ~$0.17/hr
  Use: Text detection (lightweight)

# GPU:
- Instance: g4dn.xlarge
  vCPU: 4
  RAM: 16 GB
  GPU: 1x NVIDIA T4 (16GB)
  Cost: ~$0.526/hr
  Use: Image/Audio detection
```

### Google Cloud

```yaml
# Recommended GCE instances
# CPU-only:
- Instance: n2-standard-4
  vCPU: 4
  RAM: 16 GB
  Cost: ~$0.19/hr

# GPU:
- Instance: n1-standard-4 + T4
  vCPU: 4
  RAM: 15 GB
  GPU: 1x NVIDIA T4
  Cost: ~$0.45/hr
```

### Docker Optimization

```dockerfile
# Optimized Dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install with specific extras
RUN pip install --no-cache-dir veridex[text,audio]

# Pre-download models (optional)
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('gpt2')"

# Set cache location
ENV HF_HOME=/app/cache
VOLUME /app/cache

CMD ["python", "app.py"]
```

---

## Monitoring & Profiling

### Track Performance Metrics

```python
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.metrics = []
    
    def monitor(self, detector, input_data):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024**2  # MB
        
        result = detector.run(input_data)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024**2
        
        metrics = {
            'latency_ms': (end_time - start_time) * 1000,
            'memory_mb': end_memory - start_memory,
            'detector': detector.__class__.__name__
        }
        
        self.metrics.append(metrics)
        return result
    
    def report(self):
        import pandas as pd
        df = pd.DataFrame(self.metrics)
        print(df.groupby('detector').agg({
            'latency_ms': ['mean', 'std', 'min', 'max'],
            'memory_mb': ['mean', 'max']
        }))
```

---

## Next Steps

- [Use Cases](use_cases.md) - Real-world applications
- [API Reference](api/core.md) - Complete API documentation
- [Troubleshooting](troubleshooting.md) - Common issues
- [FAQ](faq.md) - Frequently asked questions
