"""
Text Detection Examples from Documentation

This file contains all the code examples from docs/tutorials/text_detection_guide.md
These examples demonstrate comprehensive text detection capabilities.

Source: docs/tutorials/text_detection_guide.md
"""


def example_1_perplexity_signal():
    """PerplexitySignal - Recommended for general-purpose text detection"""
    from veridex.text import PerplexitySignal

    detector = PerplexitySignal(model_id="gpt2")
    result = detector.run("The artificial intelligence has revolutionized modern computing.")

    print(f"AI Probability: {result.score:.2%}")
    print(f"Mean Perplexity: {result.metadata['mean_perplexity']:.2f}")


def example_2_binoculars_signal():
    """BinocularsSignal - Highest accuracy"""
    from veridex.text import BinocularsSignal

    detector = BinocularsSignal()
    result = detector.run("Your text to analyze...")

    print(f"AI Probability: {result.score:.2%}")
    print(f"Binoculars Score: {result.metadata.get('binoculars_score', 'N/A')}")


def example_3_zlib_entropy_signal():
    """ZlibEntropySignal - Fastest"""
    from veridex.text import ZlibEntropySignal

    detector = ZlibEntropySignal()
    result = detector.run("Your text here...")

    print(f"AI Probability: {result.score:.2%}")
    print(f"Compression Ratio: {result.metadata.get('compression_ratio', 'N/A')}")


def example_4_stylometric_signal():
    """StylometricSignal - Style and pattern analysis"""
    from veridex.text import StylometricSignal

    detector = StylometricSignal()
    result = detector.run("Your text here...")

    print(f"AI Probability: {result.score:.2%}")
    print(f"Stylometric Features: {result.metadata}")


def example_5_analyzing_student_essays():
    """Practical Example 1: Analyzing Student Essays"""
    from veridex.text import PerplexitySignal

    detector = PerplexitySignal()

    essay = """
    The impact of climate change on global ecosystems represents one of 
    the most pressing challenges of our time. Rising temperatures, shifting 
    precipitation patterns, and increased frequency of extreme weather events 
    are fundamentally altering the delicate balance of nature.
    """

    result = detector.run(essay)

    if result.score > 0.7 and result.confidence > 0.6:
        print("⚠️  High probability of AI-generated content")
    elif result.score > 0.3:
        print("⚠️  Uncertain - recommend manual review")
    else:
        print("✓ Likely human-written")

    print(f"\nDetailed Results:")
    print(f"  AI Probability: {result.score:.2%}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Perplexity: {result.metadata['mean_perplexity']:.2f}")


def example_6_batch_processing():
    """Practical Example 2: Batch Processing"""
    from veridex.text import PerplexitySignal
    import pandas as pd

    detector = PerplexitySignal()

    texts = [
        "AI-generated text example 1...",
        "Human-written text example 2...",
        "Another text to analyze...",
    ]

    results = []
    for i, text in enumerate(texts):
        result = detector.run(text)
        results.append({
            'text_id': i,
            'score': result.score,
            'confidence': result.confidence,
            'perplexity': result.metadata.get('mean_perplexity', 0)
        })

    df = pd.DataFrame(results)
    print(df)


def example_7_ensemble_approach():
    """Practical Example 3: Ensemble Approach"""
    from veridex.text import PerplexitySignal, ZlibEntropySignal, StylometricSignal

    text = "Your text to analyze..."

    # Run multiple detectors
    detectors = [
        PerplexitySignal(),
        ZlibEntropySignal(),
        StylometricSignal()
    ]

    scores = []
    confidences = []

    for detector in detectors:
        result = detector.run(text)
        scores.append(result.score)
        confidences.append(result.confidence)
        print(f"{detector.__class__.__name__}: {result.score:.2%}")

    # Simple weighted average
    avg_score = sum(scores) / len(scores)
    avg_confidence = sum(confidences) / len(confidences)

    print(f"\nEnsemble Result:")
    print(f"  Average Score: {avg_score:.2%}")
    print(f"  Average Confidence: {avg_confidence:.2%}")


def preprocess_text(text):
    """Text Preprocessing Function"""
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Minimum length check
    if len(text.split()) < 10:
        print("Warning: Text too short for reliable detection")
    
    return text


def example_8_handle_short_texts():
    """Handle Short Texts Carefully"""
    from veridex.text import PerplexitySignal

    detector = PerplexitySignal()
    text = "Short text here"

    result = detector.run(text)

    if len(text.split()) < 50:
        print("⚠️  Warning: Short text may give unreliable results")
        if result.confidence < 0.5:
            print("  → Consider this result uncertain")


def comprehensive_text_check(text):
    """Use Multiple Signals for robust detection"""
    from veridex.text import PerplexitySignal, ZlibEntropySignal
    
    # Quick filter first
    quick_detector = ZlibEntropySignal()
    quick_result = quick_detector.run(text)
    
    if quick_result.score < 0.3:
        # Likely human, skip expensive check
        return quick_result
    
    # Run more accurate detector
    accurate_detector = PerplexitySignal()
    return accurate_detector.run(text)


if __name__ == "__main__":
    print("=" * 60)
    print("Text Detection Examples from Documentation")
    print("=" * 60)
    
    print("\n### Example 1: PerplexitySignal ###")
    try:
        example_1_perplexity_signal()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n### Example 3: ZlibEntropySignal (Fastest) ###")
    try:
        example_3_zlib_entropy_signal()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n### Example 5: Analyzing Student Essays ###")
    try:
        example_5_analyzing_student_essays()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nNote: Some examples require additional dependencies and may fail if not installed.")
