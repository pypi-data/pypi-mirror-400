"""
Text detection module for AI-generated text content.

Provides detectors for identifying synthetic text:
- ZlibEntropySignal: Compression-based entropy analysis
- PerplexitySignal: LLM-based perplexity analysis
"""

from .entropy import ZlibEntropySignal
from .perplexity import PerplexitySignal
from .detectgpt import DetectGPTSignal
from .tdetect import TDetectSignal
from .human_ood import HumanOODSignal
from .binoculars import BinocularsSignal
from .stylometry import StylometricSignal

__all__ = [
    "ZlibEntropySignal",
    "PerplexitySignal",
    "DetectGPTSignal",
    "TDetectSignal",
    "HumanOODSignal",
    "BinocularsSignal",
    "StylometricSignal"
]
