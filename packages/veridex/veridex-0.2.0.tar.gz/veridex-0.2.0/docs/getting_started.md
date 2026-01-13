# Getting Started

## Installation

Veridex is designed to be lightweight with optional heavy dependencies.

### Basic Installation

To install the core library (lightweight, only numpy/scipy):

```bash
pip install veridex
```

### Full Installation

To install support for all modalities (Text, Image, Audio):

```bash
pip install "veridex[text,image,audio]"
```

### Specific Modalities

- **Text**: `pip install "veridex[text]"`
- **Image**: `pip install "veridex[image]"`
- **Audio**: `pip install "veridex[audio]"`

## Usage

### Basic Usage

```python
from veridex.core import Signal
from veridex.text import PerplexitySignal

# Initialize a signal
signal = PerplexitySignal()

# Run detection
result = signal.detect("This is some text to analyze.")

print(f"Score: {result.score}")
print(f"Confidence: {result.confidence}")
print(f"Metadata: {result.metadata}")
```

### Using Multiple Signals

You can combine multiple signals to get a more robust detection result. (Fusion layer documentation coming soon).
