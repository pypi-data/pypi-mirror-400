"""
Ensemble Detection Examples from Documentation

This file contains all the code examples from docs/tutorials/ensemble_detection.md
These examples demonstrate how to combine multiple signals for robust detection.

Source: docs/tutorials/ensemble_detection.md
"""


def example_1_simple_averaging():
    """Basic Ensemble Approach - Simple Averaging"""
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

    # Calculate ensemble result
    ensemble_score = sum(scores) / len(scores)
    ensemble_confidence = sum(confidences) / len(confidences)

    print(f"Ensemble Score: {ensemble_score:.2%}")
    print(f"Ensemble Confidence: {ensemble_confidence:.2%}")


def weighted_ensemble(text):
    """Weighted Ensemble - Weight detectors by their accuracy"""
    from veridex.text import PerplexitySignal, ZlibEntropySignal, StylometricSignal
    
    # Weights based on accuracy benchmarks
    weights = {
        'perplexity': 0.5,
        'zlib': 0.2,
        'stylometric': 0.3
    }
    
    perp_detector = PerplexitySignal()
    zlib_detector = ZlibEntropySignal()
    style_detector = StylometricSignal()
    
    perp_result = perp_detector.run(text)
    zlib_result = zlib_detector.run(text)
    style_result = style_detector.run(text)
    
    weighted_score = (
        perp_result.score * weights['perplexity'] +
        zlib_result.score * weights['zlib'] +
        style_result.score * weights['stylometric']
    )
    
    return weighted_score


def confidence_voting(text, confidence_threshold=0.6):
    """Confidence-Based Voting - Only use high-confidence results"""
    from veridex.text import PerplexitySignal, ZlibEntropySignal, StylometricSignal
    
    detectors = [
        PerplexitySignal(),
        ZlibEntropySignal(),
        StylometricSignal()
    ]
    
    high_confidence_scores = []
    
    for detector in detectors:
        result = detector.run(text)
        if result.confidence >= confidence_threshold:
            high_confidence_scores.append(result.score)
    
    if not high_confidence_scores:
        return None  # No confident predictions
    
    return sum(high_confidence_scores) / len(high_confidence_scores)


def multimodal_detection(content):
    """Multi-Modal Ensemble - Combine text, image, and audio"""
    from veridex.text import PerplexitySignal
    from veridex.image import FrequencySignal
    from veridex.audio import SpectralSignal
    
    results = {}
    
    if content.get('text'):
        text_detector = PerplexitySignal()
        results['text'] = text_detector.run(content['text'])
    
    if content.get('image'):
        image_detector = FrequencySignal()
        results['image'] = image_detector.run(content['image'])
    
    if content.get('audio'):
        audio_detector = SpectralSignal()
        results['audio'] = audio_detector.run(content['audio'])
    
    # Combine scores
    scores = [r.score for r in results.values()]
    avg_score = sum(scores) / len(scores)
    
    return {
        'score': avg_score,
        'modality_scores': {k: v.score for k, v in results.items()}
    }


class ProductionDetector:
    """Production Pipeline - Two-stage detection with fast filter"""
    
    def __init__(self):
        from veridex.text import ZlibEntropySignal, PerplexitySignal, StylometricSignal
        
        # Fast filter
        self.filter = ZlibEntropySignal()
        # Accurate detectors
        self.detectors = [
            PerplexitySignal(),
            StylometricSignal()
        ]
    
    def detect(self, text):
        # Stage 1: Quick filter
        quick_result = self.filter.run(text)
        
        if quick_result.score < 0.2:
            return quick_result  # Clearly human
        
        # Stage 2: Ensemble of accurate detectors
        scores = []
        confidences = []
        
        for detector in self.detectors:
            result = detector.run(text)
            scores.append(result.score)
            confidences.append(result.confidence)
        
        # Weighted by confidence
        total_confidence = sum(confidences)
        weighted_score = sum(
            s * c / total_confidence 
            for s, c in zip(scores, confidences)
        )
        
        return {
            'score': weighted_score,
            'confidence': sum(confidences) / len(confidences)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Ensemble Detection Examples from Documentation")
    print("=" * 60)
    
    print("\n### Example 1: Simple Averaging ###")
    try:
        example_1_simple_averaging()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n### Example 2: Weighted Ensemble ###")
    try:
        score = weighted_ensemble("Sample text for ensemble detection")
        print(f"Weighted Score: {score:.2%}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n### Example 5: Production Pipeline ###")
    try:
        detector = ProductionDetector()
        result = detector.detect("Sample production text")
        print(f"Production Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
