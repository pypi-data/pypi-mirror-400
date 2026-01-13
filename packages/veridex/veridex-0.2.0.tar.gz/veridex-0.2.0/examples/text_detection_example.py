"""
Example usage of text detection in veridex.

This example demonstrates how to use the text detection module
to analyze text for AI-generated content.
"""

def example_zlib_entropy():
    """Example: Lightweight compression-based detection."""
    from veridex.text import ZlibEntropySignal, StylometricSignal
    
    # Initialize detector (no dependencies required)
    detector = ZlibEntropySignal()
    
    # Analyze text
    human_text = """
    The quick brown fox jumps over the lazy dog. This sentence has
    natural variation and complexity that human writers typically produce.
    We make mistakes, we use varied vocabulary, and our writing has
    personality!
    """
    
    ai_text = """
    The implementation of artificial intelligence systems requires
    sophisticated algorithms and comprehensive data processing. These
    systems utilize advanced machine learning techniques to optimize
    performance and deliver accurate results across various applications.
    """
    
    print("=" * 60)
    print("Zlib Entropy Detection (Compression-Based)")
    print("=" * 60)
    
    result_human = detector.run(human_text)
    print(f"\nHuman Text:")
    print(f"  AI Probability: {result_human.score:.2f}")
    print(f"  Compression Ratio: {result_human.metadata['compression_ratio']:.2f}")
    
    result_ai = detector.run(ai_text)
    print(f"\nAI-like Text:")
    print(f"  AI Probability: {result_ai.score:.2f}")
    print(f"  Compression Ratio: {result_ai.metadata['compression_ratio']:.2f}")


def example_stylometric():
    """Example: Stylometric analysis (vocabulary richness)."""
    from veridex.text import StylometricSignal
    
    print("\n" + "=" * 60)
    print("Stylometric Analysis (Linguistic Features)")
    print("=" * 60)
    
    detector = StylometricSignal()
    
    text = """
    The rapid advancement of deep learning frameworks has precipitated 
    a paradigm shift in computational linguistics. Neural architectures 
    now demonstrate capabilities that were previously considered unique 
    to biological intelligence.
    """
    
    result = detector.run(text)
    
    print(f"\nAI Probability: {result.score:.2f}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Metrics:")
    print(f"  Type-Token Ratio: {result.metadata['type_token_ratio']:.2f}")
    print(f"  Avg Sentence Length: {result.metadata['avg_sentence_length']:.2f}")
    print(f"  Special Char Ratio: {result.metadata['special_char_ratio']:.2f}")


def example_perplexity():
    """Example: Perplexity and Burstiness analysis (requires transformers)."""
    from veridex.text import PerplexitySignal
    
    # Initialize with GPT-2 (default)
    detector = PerplexitySignal(model_id="gpt2")
    
    text = """
    Artificial intelligence has revolutionized numerous industries,
    from healthcare to finance. Machine learning algorithms analyze
    vast amounts of data to identify patterns and make predictions.
    """
    
    print("\n" + "=" * 60)
    print("Perplexity & Burstiness Detection")
    print("=" * 60)
    
    result = detector.run(text)
    
    if result.error:
        print(f"\n⚠️  Error: {result.error}")
        print("   Install text dependencies: pip install veridex[text]")
    else:
        print(f"\nAI Probability: {result.score:.2f}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"\nMetrics:")
        print(f"  Mean Perplexity: {result.metadata['mean_perplexity']:.2f}")
        print(f"  Burstiness (StdDev): {result.metadata['burstiness']:.2f}")
        print(f"  Sentence Count: {result.metadata['sentence_count']}")
        print(f"  Model: {result.metadata['model_id']}")
        
        # Interpretation
        print(f"\n💡 Interpretation:")
        if result.metadata['mean_perplexity'] < 30:
            print("   Low perplexity suggests AI-generated text")
        else:
            print("   High perplexity suggests human-written text")
        
        if result.metadata['burstiness'] < 5:
            print("   Low burstiness (uniform) suggests AI-generated")
        else:
            print("   High burstiness (varied) suggests human-written")


def example_binoculars():
    """Example: Advanced Binoculars detection (requires heavy models)."""
    from veridex.text import BinocularsSignal
    
    print("\n" + "=" * 60)
    print("Binoculars Detection (Contrastive Perplexity)")
    print("=" * 60)
    
    # Initialize (will download models on first use)
    detector = BinocularsSignal()
    
    text = """
    Climate change represents one of the most significant challenges
    facing humanity in the twenty-first century. The scientific consensus
    indicates that anthropogenic greenhouse gas emissions are the primary
    driver of observed warming trends.
    """
    
    result = detector.run(text)
    
    if result.error:
        print(f"\n⚠️  Error: {result.error}")
        print("   This requires downloading ~7GB of models")
        print("   Install: pip install veridex[text]")
    else:
        print(f"\nAI Probability: {result.score:.2f}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Binoculars Score: {result.metadata.get('binoculars_score', 'N/A')}")


def example_multi_detector():
    """Example: Using multiple detectors for robust detection."""
    from veridex.text import ZlibEntropySignal, PerplexitySignal
    
    text = """
    The integration of advanced computational methodologies facilitates
    enhanced operational efficiency. Organizations leverage data-driven
    insights to optimize strategic decision-making processes and achieve
    measurable outcomes across key performance indicators.
    """
    
    print("\n" + "=" * 60)
    print("Multi-Detector Ensemble")
    print("=" * 60)
    
    # Run multiple detectors
    detectors = {
        "Entropy": ZlibEntropySignal(),
        "Perplexity": PerplexitySignal(),
    }
    
    scores = []
    print(f"\nAnalyzing text...")
    
    for name, detector in detectors.items():
        result = detector.run(text)
        
        if result.error:
            print(f"  {name}: SKIPPED ({result.error.split('.')[0]})")
        else:
            print(f"  {name}: {result.score:.2f} (confidence: {result.confidence:.2f})")
            scores.append(result.score)
    
    if scores:
        ensemble_score = sum(scores) / len(scores)
        print(f"\n📊 Ensemble Score: {ensemble_score:.2f}")
        
        if ensemble_score > 0.7:
            print("   Verdict: Likely AI-generated")
        elif ensemble_score > 0.4:
            print("   Verdict: Uncertain (may be AI-assisted)")
        else:
            print("   Verdict: Likely human-written")


def example_batch_analysis():
    """Example: Analyzing multiple text samples."""
    from veridex.text import ZlibEntropySignal
    
    texts = {
        "Sample 1": "The cat sat on the mat. It was a sunny day!",
        "Sample 2": "The implementation of distributed systems requires careful consideration of network latency and fault tolerance mechanisms.",
        "Sample 3": "I love pizza! Especially with extra cheese and pepperoni. Yum.",
    }
    
    print("\n" + "=" * 60)
    print("Batch Text Analysis")
    print("=" * 60)
    
    detector = ZlibEntropySignal()
    
    for name, text in texts.items():
        result = detector.run(text)
        status = "🤖 AI" if result.score > 0.5 else "👤 HUMAN"
        print(f"\n{name}: {status} (score: {result.score:.2f})")
        print(f"  \"{text[:50]}...\"")


if __name__ == "__main__":
    print("=" * 60)
    print("TEXT DETECTION EXAMPLES")
    print("=" * 60)
    
    # 1. Lightweight entropy detection (always works)
    example_zlib_entropy()
    
    # 2. Stylometric analysis (fast, no dependencies)
    example_stylometric()
    
    # 3. Perplexity detection (requires transformers)
    example_perplexity()
    
    # 4. Advanced Binoculars (requires heavy models)
    # example_binoculars()  # Uncomment if you have models installed
    
    # 4. Multi-detector ensemble
    example_multi_detector()
    
    # 5. Batch analysis
    example_batch_analysis()
    
    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  • Use ZlibEntropy for quick checks (no dependencies)")
    print("  • Use Perplexity for better accuracy (requires transformers)")
    print("  • Combine multiple detectors for robustness")
    print("  • Check result.error before using result.score")
