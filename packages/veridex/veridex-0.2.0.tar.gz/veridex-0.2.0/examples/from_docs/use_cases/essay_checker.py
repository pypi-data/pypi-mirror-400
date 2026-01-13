"""
Essay Checker Use Case

This file contains the EssayChecker class implementation from docs/use_cases.md
Use case: Educational institutions detecting AI-generated student submissions.

Source: docs/use_cases.md (lines 82-130)
"""

from veridex.text import BinocularsSignal, PerplexitySignal


class EssayChecker:
    """Academic integrity checker for student essays"""
    
    def __init__(self):
        # Use high-accuracy detector for academic use
        self.primary_detector = BinocularsSignal(observer_id="distilgpt2", performer_id="gpt2")
        self.secondary_detector = PerplexitySignal()
    
    def analyze_essay(self, essay_text):
        """
        Analyze student essay for AI generation probability
        
        Args:
            essay_text: str - The essay text to analyze
            
        Returns:
            dict: Analysis result with status, recommendation, and details
        """
        # Run both detectors
        primary_result = self.primary_detector.run(essay_text)
        secondary_result = self.secondary_detector.run(essay_text)
        
        # Ensemble decision
        avg_score = (primary_result.score + secondary_result.score) / 2
        avg_confidence = (primary_result.confidence + secondary_result.confidence) / 2
        
        # Conservative thresholds for academic use
        if avg_score > 0.85 and avg_confidence > 0.75:
            return {
                'status': 'LIKELY_AI_GENERATED',
                'recommendation': 'MANUAL_REVIEW_REQUIRED',
                'confidence': avg_confidence,
                'details': {
                    'binoculars_score': primary_result.score,
                    'perplexity_score': secondary_result.score,
                    'perplexity': primary_result.metadata.get('mean_perplexity')
                }
            }
        elif avg_score > 0.6:
            return {
                'status': 'UNCERTAIN',
                'recommendation': 'CONSIDER_INTERVIEW',
                'confidence': avg_confidence
            }
        else:
            return {
                'status': 'LIKELY_HUMAN_WRITTEN',
                'confidence': avg_confidence
            }


if __name__ == "__main__":
    print("=" * 60)
    print("Essay Checker Use Case Example")
    print("=" * 60)
    
    # Usage example
    checker = EssayChecker()
    
    student_essay = """
    The impact of artificial intelligence on modern society represents
    a transformative shift in how we approach problem-solving and decision-making.
    Machine learning algorithms have demonstrated remarkable capabilities...
    """
    
    try:
        result = checker.analyze_essay(student_essay)
        
        if result['status'] == 'LIKELY_AI_GENERATED':
            print(f"⚠️  Essay flagged for review (confidence: {result['confidence']:.2%})")
        else:
            print(f"Status: {result['status']}")
            print(f"Confidence: {result['confidence']:.2%}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nEthical Considerations:")
    print("- Never use as sole evidence for academic misconduct")
    print("- Always provide students opportunity to explain")
    print("- Combine with other indicators (writing style changes, interview)")
    print("- Be transparent about detection methods used")
    print("- Regularly update detectors as AI models evolve")
