"""
Quick Start Examples from Documentation

This file contains all the code examples from docs/tutorials/quick_start.md
These examples demonstrate basic usage of Veridex across all three modalities.

Source: docs/tutorials/quick_start.md
"""

def example_1_basic_text_detection():
    """Basic text detection with PerplexitySignal"""
    from veridex.text import PerplexitySignal

    detector = PerplexitySignal()
    result = detector.run("The artificial intelligence landscape has evolved dramatically.")

    print(f"AI Probability: {result.score:.2%}")
    print(f"Confidence: {result.confidence:.2%}")


def example_2_basic_image_detection():
    """Basic image detection with FrequencySignal"""
    from veridex.image import FrequencySignal

    detector = FrequencySignal()
    result = detector.run("path/to/image.png")

    print(f"AI Probability: {result.score:.2%}")
    print(f"Confidence: {result.confidence:.2%}")


def example_3_basic_audio_detection():
    """Basic audio detection with SpectralSignal"""
    from veridex.audio import SpectralSignal

    detector = SpectralSignal()
    result = detector.run("path/to/audio.wav")

    print(f"AI Probability: {result.score:.2%}")
    print(f"Confidence: {result.confidence:.2%}")


def example_4_understanding_results():
    """Understanding DetectionResult structure"""
    from veridex.text import PerplexitySignal
    
    detector = PerplexitySignal()
    result = detector.run("Sample text for analysis")

    # Core fields
    print(f"Score: {result.score}")        # 0.0-1.0: Probability of AI-generated content
    print(f"Confidence: {result.confidence}")   # 0.0-1.0: How confident the detector is
    print(f"Metadata: {result.metadata}")     # Dict with additional metrics


def example_5_text_metadata():
    """Exploring metadata for text detection"""
    from veridex.text import PerplexitySignal
    
    detector = PerplexitySignal()
    result = detector.run("Your text here...")
    
    # Access metadata
    print(f"Mean Perplexity: {result.metadata['mean_perplexity']:.2f}")
    print(f"Burstiness: {result.metadata.get('burstiness', 'N/A')}")


def example_6_image_metadata():
    """Exploring metadata for image detection"""
    from veridex.image import FrequencySignal
    
    detector = FrequencySignal()
    result = detector.run("image.png")
    
    # Access metadata
    print(f"High Freq Score: {result.metadata.get('high_freq_score', 'N/A')}")


def example_7_audio_metadata():
    """Exploring metadata for audio detection"""
    from veridex.audio import SpectralSignal
    
    detector = SpectralSignal()
    result = detector.run("audio.wav")
    
    # Access metadata
    print(f"High Freq Energy: {result.metadata.get('high_freq_energy', 'N/A')}")
    print(f"Spectral Rolloff: {result.metadata.get('spectral_rolloff', 'N/A')}")


def example_8_multiple_text_detectors():
    """Try multiple text detectors"""
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


def example_9_multiple_image_detectors():
    """Try multiple image detectors"""
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


def example_10_multiple_audio_detectors():
    """Try multiple audio detectors"""
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


if __name__ == "__main__":
    print("=" * 60)
    print("Quick Start Examples from Documentation")
    print("=" * 60)
    
    print("\n### Example 1: Basic Text Detection ###")
    try:
        example_1_basic_text_detection()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n### Example 8: Multiple Text Detectors ###")
    try:
        example_8_multiple_text_detectors()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nNote: Some examples require image/audio files and have been commented out.")
    print("See the function definitions for complete examples.")
