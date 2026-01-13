import zlib
from typing import Any
from veridex.core.signal import BaseSignal, DetectionResult

class ZlibEntropySignal(BaseSignal):
    """
    Detects AI content using compression ratio (zlib entropy).

    This method employs a compression-based approach under the hypothesis that AI-generated
    content is more predictable map (lower entropy) and thus more compressible than human content.

    Algorithm:
        ratio = len(zlib(text)) / len(text)
        - Lower ratio (< 0.6) -> Highly compressible -> Likely AI.
        - Higher ratio (> 0.8) -> Less compressible -> Likely Human.

    Attributes:
        name (str): 'zlib_entropy'
        dtype (str): 'text'
    """

    @property
    def name(self) -> str:
        return "zlib_entropy"

    @property
    def dtype(self) -> str:
        return "text"

    def run(self, input_data: Any) -> DetectionResult:
        if not isinstance(input_data, str):
             return DetectionResult(
                score=0.0,
                confidence=0.0,
                metadata={},
                error="Input must be a string."
            )

        if not input_data:
             return DetectionResult(
                score=0.0,
                confidence=0.0,
                metadata={"zlib_ratio": 0.0},
                error="Input string is empty."
            )

        encoded = input_data.encode("utf-8")
        compressed = zlib.compress(encoded)
        ratio = len(compressed) / len(encoded)
        
        # Calculate confidence based on how extreme the ratio is
        # Very compressible (low ratio) or very incompressible (high ratio) = higher confidence
        # Middle values = lower confidence
        # Typical ranges: AI text ~0.55-0.70, Human text ~0.65-0.85
        if ratio < 0.6:
            # Very compressible (repetitive) - moderate confidence it's AI
            score = 0.6  # Slightly AI-leaning
        elif ratio > 0.8:
            # Not very compressible (diverse) - moderate confidence it's human
            score = 0.3  # Slightly human-leaning
        else:
            # Middle range - low confidence
            score = 0.5  # Neutral
        
        # Use distance from neutral point (0.5) as confidence indicator
        distance_from_neutral = abs(score - 0.5)
        
        # Map distance to confidence
        # Distance 0.5 (max) -> confidence ~0.45
        # Distance 0.0 (neutral) -> confidence ~0.25
        confidence = 0.25 + distance_from_neutral * 0.4  # Range: 0.25 to 0.45
        
        return DetectionResult(
            score=score,
            confidence=confidence,
            metadata={
                "original_len": len(encoded),
                "compressed_len": len(compressed),
                "compression_ratio": ratio
            }
        )
