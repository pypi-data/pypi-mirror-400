"""
Example usage of audio detection in veridex.

This example demonstrates how to use the audio detection module
to analyze audio files for AI-generated content.
"""

from pathlib import Path


def example_spectral_detection():
    """Example: Spectral analysis (lightweight, CPU-friendly)."""
    from veridex.audio import SpectralSignal
    
    # Initialize detector
    detector = SpectralSignal()
    
    # Analyze an audio file
    audio_path = "./samples/audio/sample_voice.wav"
    
    if not Path(audio_path).exists():
        print(f"⚠️  Error: Could not find audio file at {audio_path}")
        print("   Please ensure the sample audio files are downloaded.")
        return

    result = detector.run(audio_path)
    
    # Check results
    print(f"AI Probability: {result.score:.2f}")
    print(f"Confidence: {result.confidence:.2f}")
    
    if result.error:
        print(f"Error: {result.error}")
    else:
        print("\nSpectral Features:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value:.2f}")


def example_silence_detection():
    """Example: Silence and pause analysis (detects unnatural pacing)."""
    from veridex.audio import SilenceSignal
    from pathlib import Path
    
    detector = SilenceSignal()
    
    audio_path = "./samples/audio/sample_voice.wav"
    
    if not Path(audio_path).exists():
        print(f"⚠️  Error: Could not find audio file at {audio_path}")
        return

    result = detector.run(audio_path)
    
    print("\n" + "=" * 60)
    print("Silence & Pause Analysis")
    print("=" * 60)
    
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"AI Probability: {result.score:.2f}")
        print(f"Confidence: {result.confidence:.2f}")
        print("Metrics:")
        print(f"  Silence Ratio: {result.metadata['silence_ratio']:.2f}")
        print(f"  Mean Pause: {result.metadata['mean_pause_duration']:.2f}s")
        print(f"  Pause StdDev: {result.metadata['pause_duration_std']:.2f}s")
        
        print(f"\n💡 Interpretation:")
        if result.score > 0.5:
            print("   Abnormal silence patterns detected (too continuous or robotic)")
        else:
            print("   Natural pause distribution detected")


def example_wav2vec_detection():
    """Example: Wav2Vec 2.0 foundation model (high accuracy)."""
    from veridex.audio import Wav2VecSignal
    
    # Initialize with pre-trained model
    detector = Wav2VecSignal(
        model_id="nii-yamagishilab/wav2vec-large-anti-deepfake",
        use_gpu=True  # Use GPU if available
    )
    
    # Analyze audio
    audio_path = "./samples/audio/sample_voice.wav"
    
    if not Path(audio_path).exists():
        print(f"⚠️  Error: Could not find audio file at {audio_path}")
        return

    result = detector.run(audio_path)
    
    print(f"AI Probability: {result.score:.2f}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Model: {result.metadata.get('model_id', 'N/A')}")
    print(f"Duration: {result.metadata.get('audio_duration', 0):.2f}s")


def example_aasist_detection():
    """Example: AASIST spectro-temporal analysis."""
    from veridex.audio import AASISTSignal
    
    # Initialize detector
    detector = AASISTSignal()
    
    # Analyze audio
    audio_path = "./samples/audio/sample_voice.wav"
    
    if not Path(audio_path).exists():
        print(f"⚠️  Error: Could not find audio file at {audio_path}")
        return

    result = detector.run(audio_path)
    
    print(f"AI Probability: {result.score:.2f}")
    print(f"Confidence: {result.confidence:.2f}")
    
    if not result.error:
        print("\nSpectro-Temporal Features:")
        print(f"  Temporal Variation: {result.metadata['mean_temporal_variation']:.2f}")
        print(f"  Energy Uniformity: {result.metadata['energy_uniformity']:.2f}")
        print(f"  Phase Coherence: {result.metadata['phase_coherence']:.2f}")


def example_ensemble_detection():
    """Example: Using multiple detectors for robust detection."""
    from veridex.audio import SpectralSignal, AASISTSignal
    
    audio_path = "./samples/audio/sample_voice.wav"
    
    if not Path(audio_path).exists():
        print(f"⚠️  Error: Could not find audio file at {audio_path}")
        return
    
    # Run multiple detectors
    spectral = SpectralSignal()
    aasist = AASISTSignal()
    
    results = {
        "spectral": spectral.run(audio_path),
        "aasist": aasist.run(audio_path),
    }
    
    # Combine scores (simple average for demonstration)
    valid_scores = [r.score for r in results.values() if r.error is None]
    
    if valid_scores:
        ensemble_score = sum(valid_scores) / len(valid_scores)
        print(f"Ensemble AI Probability: {ensemble_score:.2f}")
        
        # Show individual results
        for name, result in results.items():
            if result.error:
                print(f"{name}: ERROR - {result.error}")
            else:
                print(f"{name}: {result.score:.2f} (confidence: {result.confidence:.2f})")
    else:
        print("All detectors failed!")


def example_batch_processing():
    """Example: Processing multiple audio files."""
    from veridex.audio import SpectralSignal
    
    detector = SpectralSignal()
    
    # Process multiple files
    audio_files = [
        "./samples/audio/sample_voice.wav",
        "./samples/audio/kalimba.wav",
    ]
    
    for audio_path in audio_files:
        result = detector.run(audio_path)
        
        if result.error:
            print(f"{audio_path}: ERROR - {result.error}")
        else:
            status = "AI" if result.score > 0.5 else "HUMAN"
            print(f"{audio_path}: {status} (score: {result.score:.2f})")


if __name__ == "__main__":
    print("=" * 60)
    print("Audio Detection Examples")
    print("=" * 60)
    
    # NOTE: These examples require audio dependencies
    # Install with: pip install veridex[audio]
    
    print("\n1. Spectral Detection (Lightweight)")
    print("-" * 60)
    try:
        example_spectral_detection()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Silence Analysis (Pause Patterns)")
    print("-" * 60)
    try:
        example_silence_detection()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. AASIST Detection (Spectro-Temporal)")
    print("-" * 60)
    try:
        example_aasist_detection()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Ensemble Detection")
    print("-" * 60)
    try:
        example_ensemble_detection()
    except Exception as e:
        print(f"Error: {e}")
