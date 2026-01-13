"""
Advanced Multimodal Detection Example.

This script demonstrates the usage of the latest advanced detection signals in Veridex:
1. Text: DetectGPT, T-Detect, HumanOOD
2. Image: CLIP Zero-Shot, MLEP (Multi-granularity Local Entropy Patterns)
3. Audio: Breathing Pattern Analysis
"""

import os
import sys
from pathlib import Path

# Ensure veridex is in path if running from examples dir
sys.path.append(str(Path(__file__).parent.parent))

from veridex.text import DetectGPTSignal, TDetectSignal, HumanOODSignal
from veridex.image import CLIPSignal, MLEPSignal
from veridex.audio import BreathingSignal

# Sample Data Paths
BASE_DIR = Path(__file__).parent.parent
SAMPLE_AUDIO_PATH = BASE_DIR / "samples" / "audio" / "sample_voice.wav"
SAMPLE_IMAGE_REAL = BASE_DIR / "samples" / "image" / "Cat_non_ai.jpg"
SAMPLE_IMAGE_AI = BASE_DIR / "samples" / "image" / "cat_ai.jpg"

def print_header(title):
    print(f"\n{'=' * 60}")
    print(f" {title.upper()}")
    print(f"{'=' * 60}")

def print_result(signal_name, result):
    print(f"\n[{signal_name}]")
    if result.error:
        print(f"  ❌ Error: {result.error}")
        return
    
    status = "🤖 AI-GENERATED" if result.score > 0.5 else "👤 HUMAN-MADE"
    print(f"  Verdict: {status}")
    print(f"  Score: {result.score:.4f}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Metadata:")
    for k, v in result.metadata.items():
        if isinstance(v, float):
            print(f"    - {k}: {v:.4f}")
        else:
            print(f"    - {k}: {v}")

def test_advanced_text():
    print_header("Text Modality: Zero-Shot Methods")

    # Sample texts
    human_text = """
    The integration of renewable energy sources into the existing power grid presents 
    both technical challenges and significant environmental opportunities. Engineers 
    must balance supply intermittency with demand fluctuations to ensure stability.
    """
    
    # Simple AI text (often has lower curvature/perplexity spikes)
    ai_text = """
    Renewable energy integration is a complex process that involves connecting 
    sustainable power sources like wind and solar to the electrical grid. 
    This allows for reduced carbon emissions but requires careful management.
    """

    detector_configs = [
        ("DetectGPT (Curvature)", DetectGPTSignal, {"base_model_name": "distilgpt2", "n_perturbations": 2, "device": "cpu"}),
        ("T-Detect (Robust)", TDetectSignal, {"base_model_name": "distilgpt2", "n_perturbations": 2, "device": "cpu"}),
        # ("HumanOOD (Distance)", HumanOODSignal, {"model_name": "distilgpt2", "n_samples": 1, "device": "cpu"})
    ]

    for name, cls, kwargs in detector_configs:
        print(f"\n🔹 Testing {name}...")
        # Instantiate and run one by one to save memory
        detector = cls(**kwargs)
        res = detector.run(ai_text)
        print_result(name, res)
        # Help GC
        del detector
        import gc
        gc.collect()

def test_advanced_image():
    print_header("Image Modality: Visual Artifacts & Semantics")

    if not SAMPLE_IMAGE_AI.exists():
        print(f"⚠️  Sample image not found at {SAMPLE_IMAGE_AI}")
        return

    detectors = [
        ("CLIP Zero-Shot", CLIPSignal()),
        ("MLEP Entropy", MLEPSignal())
    ]

    for name, detector in detectors:
        print(f"\n🔹 Testing {name} on {SAMPLE_IMAGE_AI.name}...")
        res = detector.run(str(SAMPLE_IMAGE_AI))
        print_result(name, res)

def test_advanced_audio():
    print_header("Audio Modality: Physiological Signals")

    if not SAMPLE_AUDIO_PATH.exists():
        print(f"⚠️  Sample audio not found at {SAMPLE_AUDIO_PATH}")
        return
    
    print(f"Analyzing {SAMPLE_AUDIO_PATH.name}...")

    # Breathing Detector
    detector = BreathingSignal()
    res = detector.run(str(SAMPLE_AUDIO_PATH))
    print_result("Breathing Analysis", res)

if __name__ == "__main__":
    print("Veridex Advanced Signal Demonstration")
    
    # Text
    try:
        test_advanced_text()
    except Exception as e:
        print(f"\n⚠️ Text Detection Failed: {e}")

    # Image
    try:
        test_advanced_image()
    except Exception as e:
        print(f"\n⚠️ Image Detection Failed: {e}")

    # Audio
    try:
        test_advanced_audio()
    except Exception as e:
        print(f"\n⚠️ Audio Detection Failed: {e}")

