from typing import Any
import os
import tempfile
import numpy as np
from veridex.core.signal import BaseSignal, DetectionResult

class ELASignal(BaseSignal):
    """
    Error Level Analysis (ELA) detection signal.
    
    ELA works by intentionally resaving the image at a known error rate, such as 90%, 
    then computing the difference between the original image and the resaved image. 
    If an image has not been manipulated, the error levels should be consistent.
    AI generated images or spliced images often exhibit inconsistent error levels or 
    specific compression artifacts.
    """

    @property
    def name(self) -> str:
        return "error_level_analysis"

    @property
    def dtype(self) -> str:
        return "image"

    def run(self, input_data: Any) -> DetectionResult:
        """
        Runs ELA on the input image path or PIL Image.
        """
        try:
            try:
                from PIL import Image, ImageChops
            except ImportError:
                return DetectionResult(
                    score=0.0,
                    confidence=0.0,
                    error="Pillow (PIL) is required. Install veridex[image]."
                )

            if isinstance(input_data, str):
                image = Image.open(input_data).convert('RGB')
            elif isinstance(input_data, Image.Image):
                image = input_data.convert('RGB')
            else:
                 return DetectionResult(
                    score=0.0,
                    confidence=0.0,
                    error="Input must be a file path or PIL Image."
                )
            
            # Create a temporary file to save the compressed version
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                temp_filename = tmp.name
            
            try:
                # Resave at fixed quality
                quality = 90
                image.save(temp_filename, 'JPEG', quality=quality)
                
                # Open resaved image
                resaved_image = Image.open(temp_filename)
                
                # Calculate difference
                ela_image = ImageChops.difference(image, resaved_image)
                
                # Calculate extrema (max difference)
                extrema = ela_image.getextrema()
                max_diff = max([ex[1] for ex in extrema])
                
                # Calculate simple scale score
                # If max_diff is very high, it means high compression artifacts existed 
                # or significant changes occurred on resave.
                # However, for AI detection, we often look for *lack* of standard camera block artifacts
                # or specific noise patterns.
                
                # For this baseline, we will use the mean absolute difference as a proxy for "noise level".
                # AI images (diffusion) often have high frequency noise that might react strongly to JPEG compression.
                
                np_ela = np.array(ela_image)
                mean_diff = np.mean(np_ela)
                
                # Normalize mean_diff to a 0-1 score (heuristic)
                # Assuming mean_diff > 20 is "suspicious" or "high noise"
                score = min(mean_diff / 20.0, 1.0)
                
            finally:
                # Cleanup
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

            return DetectionResult(
                score=score,
                confidence=0.5, # ELA is sensitive to format
                metadata={
                    "ela_mean_diff": float(mean_diff),
                    "ela_max_diff": float(max_diff)
                }
            )
            
        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error=f"ELA execution failed: {str(e)}"
            )
