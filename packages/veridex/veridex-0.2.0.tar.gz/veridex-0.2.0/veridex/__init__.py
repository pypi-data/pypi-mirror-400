"""
Veridex: A modular, probabilistic AI content detection library.

Veridex provides a unified interface for detecting AI-generated content across multiple
modalities (text, image, audio). It uses a signal-based architecture where multiple
independent 'signals' (detectors) analyze content and return probabilistic scores
along with interpretable metadata.

Key Features:
    - Multi-modal support (Text, Image, Audio, Video)
    - modular 'Signal' architecture
    - Probabilistic outputs with confidence scores
    - Research-grounded detection methods

Common Usage:
    >>> from veridex.text import PerplexitySignal
    >>> signal = PerplexitySignal()
    >>> result = signal.run("Some suspicious text...")
    >>> print(f"AI Probability: {result.score}")
"""

__version__ = "0.1.4"
