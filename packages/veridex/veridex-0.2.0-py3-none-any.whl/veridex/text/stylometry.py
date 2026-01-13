from typing import Any, List
import string
import math
from veridex.core.signal import BaseSignal, DetectionResult

class StylometricSignal(BaseSignal):
    """
    Analyzes stylistic features of the text such as vocabulary richness and sentence structure.
    
    This signal assumes that AI generated text often exhibits:
    - Lower vocabulary richness (Type-Token Ratio)
    - More uniform sentence lengths
    - Lower frequency of special characters/punctuation
    """

    @property
    def name(self) -> str:
        return "stylometric_analysis"

    @property
    def dtype(self) -> str:
        return "text"

    def run(self, input_data: Any) -> DetectionResult:
        """
        Runs stylometric analysis on the input text.
        """
        if not isinstance(input_data, str):
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error="Input must be a string."
            )

        text = input_data.strip()
        if not text:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                explanation="Input text is empty."
            )

        # 1. Type-Token Ratio (TTR)
        # Remove punctuation for token counting
        translator = str.maketrans('', '', string.punctuation)
        clean_text = text.translate(translator).lower()
        tokens = clean_text.split()
        
        if not tokens:
             return DetectionResult(
                score=0.0,
                confidence=0.0,
                explanation="No tokens found in text."
            )

        unique_tokens = set(tokens)
        ttr = len(unique_tokens) / len(tokens)

        # 2. Average Sentence Length (ASL)
        # Simple splitting by '.', '!', '?'
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        avg_sentence_length = len(tokens) / max(len(sentences), 1)

        # 3. Special Character Ratio
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_char_ratio = special_chars / len(text)

        # Heuristic Scoring Logic
        # These thresholds are heuristic and would ideally be calibrated on a dataset.
        # AI text often has TTR ~ 0.4-0.6 (repetitive but fluent)
        # Human text can vary wildly.
        
        # We will use a simplified heuristic:
        # Lower TTR (< 0.5) -> Higher AI probability
        # Very uniform sentence length -> difficult to measure without variance, 
        # but let's just stick to TTR as the primary driver for this simple signal.
        
        # Sigmoid-like transformation for TTR
        # If TTR is low (e.g. 0.3), score should be high.
        # If TTR is high (e.g. 0.8), score should be low.
        
        # Inverting TTR to map to "AI-ness"
        # Using a simple linear map for now: 1.0 - TTR
        # This is a naive implementation but serves as a baseline statistical feature.
        
        score = 1.0 - ttr
        
        # Clip score
        score = max(0.0, min(1.0, score))

        return DetectionResult(
            score=score,
            confidence=0.6, # Statistical methods are generally less confident than LLMs
            metadata={
                "type_token_ratio": ttr,
                "avg_sentence_length": avg_sentence_length,
                "special_char_ratio": special_char_ratio,
                "token_count": len(tokens),
                "sentence_count": len(sentences)
            }
        )
