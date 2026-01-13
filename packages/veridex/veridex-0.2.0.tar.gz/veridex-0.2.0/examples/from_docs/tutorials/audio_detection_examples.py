"""
Audio Detection Examples from Documentation

This file contains all the code examples from docs/tutorials/audio_detection_guide.md
These examples demonstrate audio detection capabilities.

Source: docs/tutorials/audio_detection_guide.md
"""


def example_1_spectral_signal():
    """SpectralSignal - Fastest"""
    from veridex.audio import SpectralSignal

    detector = SpectralSignal()
    result = detector.run("audio.wav")

    print(f"AI Probability: {result.score:.2%}")


def example_2_aasist_signal():
    """AASISTSignal - Anti-Spoofing"""
    from veridex.audio import AASISTSignal

    detector = AASISTSignal()
    result = detector.run("audio.wav")

    print(f"AI Probability: {result.score:.2%}")


def example_3_wav2vec_signal():
    """Wav2VecSignal - Highest Accuracy"""
    from veridex.audio import Wav2VecSignal

    detector = Wav2VecSignal()
    result = detector.run("audio.wav")

    print(f"AI Probability: {result.score:.2%}")


def example_4_silence_signal():
    """SilenceSignal - Pattern Analysis"""
    from veridex.audio import SilenceSignal

    detector = SilenceSignal()
    result = detector.run("audio.wav")

    print(f"AI Probability: {result.score:.2%}")


if __name__ == "__main__":
    print("=" * 60)
    print("Audio Detection Examples from Documentation")
    print("=" * 60)
    
    print("\n### Example 1: SpectralSignal (Fastest) ###")
    try:
        example_1_spectral_signal()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n### Example 4: SilenceSignal ###")
    try:
        example_4_silence_signal()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nNote: These examples require audio files to run successfully.")
    print("Please provide path to actual audio (.wav) files in the function calls.")
