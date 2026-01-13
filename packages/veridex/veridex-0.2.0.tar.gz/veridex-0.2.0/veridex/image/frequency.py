import numpy as np
from typing import Any, Dict, Optional
from veridex.core.signal import BaseSignal, DetectionResult

class FrequencySignal(BaseSignal):
    """
    Detects AI images using frequency domain analysis (FFT).

    AI-generated images often exhibit specific artifacts in the frequency domain,
    such as regular grid-like patterns (checkerboard artifacts) from upsampling layers
    or anomalous power distributions compared to natural images.

    This signal computes the Fourier Transform of the image and extracts features like:
    - Mean frequency magnitude
    - High-frequency energy ratio
    - Variance of the Laplacian (sharpness/texture)

    Attributes:
        name (str): 'frequency_artifacts'
        dtype (str): 'image'
    """

    @property
    def name(self) -> str:
        return "frequency_artifacts"

    @property
    def dtype(self) -> str:
        return "image"

    def check_dependencies(self) -> None:
        try:
            import cv2
            import numpy
        except ImportError as e:
            raise ImportError(
                "FrequencySignal requires 'opencv-python-headless' and 'numpy'. "
                "Install with `pip install veridex[image]`"
            ) from e

    def run(self, input_data: Any) -> DetectionResult:
        """
        Input data should be a path to an image or a numpy array/PIL Image.
        For simplicity, we assume input_data is a file path or a PIL Image.
        """
        try:
            import cv2
            from PIL import Image
        except ImportError:
            self.check_dependencies()
            # If check_dependencies passed but import fails (unlikely), re-raise
            raise

        img_array = None

        # Handle input types
        if isinstance(input_data, str):
            try:
                # Load as grayscale
                img_array = cv2.imread(input_data, cv2.IMREAD_GRAYSCALE)
                if img_array is None:
                    return DetectionResult(
                        score=0.0,
                        confidence=0.0,
                        metadata={},
                        error=f"Could not read image from path: {input_data}"
                    )
            except Exception as e:
                return DetectionResult(
                     score=0.0,
                     confidence=0.0,
                     metadata={},
                     error=f"Error reading image path: {str(e)}"
                )
        elif isinstance(input_data, Image.Image):
            # Convert PIL to grayscale numpy array
            img_array = np.array(input_data.convert("L"))
        elif isinstance(input_data, np.ndarray):
             # Assume it's an image array. If 3 channels, convert to gray.
             if len(input_data.shape) == 3:
                 img_array = cv2.cvtColor(input_data, cv2.COLOR_BGR2GRAY)
             else:
                 img_array = input_data
        else:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                metadata={},
                error="Input must be a file path, PIL Image, or numpy array."
            )

        # 1. FFT
        f = np.fft.fft2(img_array)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)

        # 2. Calculate metrics
        # Mean frequency magnitude
        mean_magnitude = np.mean(magnitude_spectrum)

        # High frequency ratio (heuristic)
        rows, cols = img_array.shape
        crow, ccol = rows // 2, cols // 2
        # Mask low frequencies (center)
        mask_size = min(rows, cols) // 8
        fshift_high = fshift.copy()
        fshift_high[crow - mask_size:crow + mask_size, ccol - mask_size:ccol + mask_size] = 0

        high_freq_energy = np.sum(np.abs(fshift_high))
        total_energy = np.sum(np.abs(fshift))

        high_freq_ratio = high_freq_energy / (total_energy + 1e-8)

        # Variance of Laplacian (blur detection / high freq texture)
        laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()

        # Heuristic scoring (placeholder logic)
        # Real images often have specific 1/f decay.
        # AI images might have higher high-freq energy due to upsampling artifacts (checkerboard)
        # OR they might be overly smooth (low laplacian var).
        # This is highly model dependent.
        # For now, we return a neutral score but provide rich metadata.
        # Confidence is low (0.3) since this is raw heuristic without trained model

        return DetectionResult(
            score=0.5,
            confidence=0.3,  # Low confidence - heuristic frequency analysis
            metadata={
                "mean_magnitude": float(mean_magnitude),
                "high_freq_ratio": float(high_freq_ratio),
                "laplacian_variance": float(laplacian_var),
                "image_shape": img_array.shape
            }
        )
