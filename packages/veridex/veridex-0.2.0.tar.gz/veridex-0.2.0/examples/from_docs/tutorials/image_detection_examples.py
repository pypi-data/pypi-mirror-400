"""
Image Detection Examples from Documentation

This file contains all the code examples from docs/tutorials/image_detection_guide.md
These examples demonstrate image detection capabilities.

Source: docs/tutorials/image_detection_guide.md
"""


def example_1_frequency_domain_signal():
    """FrequencySignal - Recommended for Quick Screening"""
    from veridex.image import FrequencySignal

    detector = FrequencySignal()
    result = detector.run("image.png")

    print(f"AI Probability: {result.score:.2%}")


def example_2_dire_signal():
    """DIRESignal - Highest Accuracy (requires GPU)"""
    from veridex.image import DIRESignal

    detector = DIRESignal()
    result = detector.run("image.png")

    print(f"AI Probability: {result.score:.2%}")


def example_3_ela_signal():
    """ELASignal - Manipulation Detection"""
    from veridex.image import ELASignal

    detector = ELASignal()
    result = detector.run("image.png")

    print(f"AI Probability: {result.score:.2%}")


if __name__ == "__main__":
    print("=" * 60)
    print("Image Detection Examples from Documentation")
    print("=" * 60)
    
    print("\n### Example 1: FrequencySignal ###")
    try:
        example_1_frequency_domain_signal()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nNote: These examples require image files to run successfully.")
    print("Please provide path to actual image files in the function calls.")
