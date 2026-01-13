
import math
import numpy as np
import scipy.stats
from typing import Optional
from veridex.core.signal import DetectionResult
from veridex.text.detectgpt import DetectGPTSignal

class TDetectSignal(DetectGPTSignal):
    """
    Implements T-Detect (West et al., 2025), a robust variant of DetectGPT.

    Instead of assuming a Gaussian distribution for perturbations (Z-score),
    T-Detect uses a Student's t-distribution to better model the heavy-tailed
    nature of adversarial or non-native text perturbations.
    """

    @property
    def name(self) -> str:
        return "t_detect"

    def check_dependencies(self) -> None:
        super().check_dependencies()
        try:
            import scipy
        except ImportError:
            raise ImportError(
                "T-Detect signal requires 'scipy'. Please install it via `pip install scipy`."
            )

    def run(self, input_data: str) -> DetectionResult:
        # Reuse the logic to get perturbations and LLs
        if not input_data or not isinstance(input_data, str):
            return DetectionResult(score=0.0, confidence=0.0, error="Invalid input")

        self._load_models()

        original_ll = self._get_ll(input_data)
        perturbations = self._perturb_text_flan(input_data)

        perturbed_lls = []
        for p_text in perturbations:
            if not p_text.strip():
                continue
            ll = self._get_ll(p_text)
            perturbed_lls.append(ll)

        if not perturbed_lls:
            return DetectionResult(score=0.0, confidence=0.0, error="Failed to generate valid perturbations")

        # T-Detect Logic
        mu_p = np.mean(perturbed_lls)
        std_p = np.std(perturbed_lls) if len(perturbed_lls) > 1 else 1.0

        # Degrees of freedom = n - 1
        df = max(1, len(perturbed_lls) - 1)

        curvature = original_ll - mu_p

        # t-score calculation
        t_score = curvature / (std_p + 1e-8)

        # Convert t_score to scalar float safely
        try:
            if isinstance(t_score, (np.ndarray, np.generic)):
                t_score = float(t_score.item()) if isinstance(t_score, np.ndarray) and t_score.size == 1 else float(t_score)
        except Exception:
            # Fallback for unexpected numpy shapes, though unlikely
            t_score = float(np.mean(t_score))

        # Calculate probability using T-CDF
        # If it's AI, curvature is positive (original >> perturbed).
        # We assume 'prob' is the probability that the text is AI.
        # High t_score -> High probability.
        prob = scipy.stats.t.cdf(t_score, df)

        # Ensure prob is scalar float safely
        try:
            if isinstance(prob, (np.ndarray, np.generic)):
                prob = float(prob.item()) if isinstance(prob, np.ndarray) and prob.size == 1 else float(prob)
        except Exception:
             prob = float(np.mean(prob))

        if math.isnan(prob):
             prob = 0.5

        # Calculate confidence from measurement uncertainty (similar to DetectGPT)
        # T-Detect is slightly more robust, so base confidence is a bit higher
        if std_p < 0.2:
            confidence = 0.92
        elif std_p < 0.5:
            confidence = 0.85
        elif std_p < 1.0:
            confidence = 0.75
        elif std_p < 2.0:
            confidence = 0.55
        else:
            confidence = 0.35
        
        if len(perturbed_lls) >= 15:
            confidence = min(confidence + 0.05, 0.95)

        return DetectionResult(
            score=float(prob),
            confidence=confidence,
            metadata={
                "original_ll": float(original_ll),
                "perturbed_mean_ll": float(mu_p),
                "perturbed_std_ll": float(std_p),
                "curvature": float(curvature),
                "t_score": float(t_score),
                "df": int(df),
                "n_perturbations": len(perturbed_lls)
            }
        )
