import math
import numpy as np
from typing import Any, List, Optional
from veridex.core.signal import BaseSignal, DetectionResult

class DetectGPTSignal(BaseSignal):
    """
    Implements the DetectGPT zero-shot detection method (Mitchell et al., 2023).

    It operates on the hypothesis that LLM-generated text lies in negative curvature regions
    of the model's log probability function. By perturbing the text (using a mask-filling model like T5)
    and comparing the log-likelihood of the original text vs. perturbed texts, we can distinguish
    AI text (high curvature drop) from human text.
    """

    def __init__(
        self,
        base_model_name: str = "gpt2-medium",
        perturbation_model_name: str = "t5-base",
        n_perturbations: int = 15,
        pct_words_masked: float = 0.3,
        span_length: int = 2,
        seed: int = 42,
        device: Optional[str] = None
    ):
        """
        Args:
            base_model_name: Name of the model used to compute likelihoods (e.g., 'gpt2', 'gpt2-medium', 'gpt-neo-2.7B').
            perturbation_model_name: Name of the model used to generate perturbations (e.g., 't5-base', 't5-small').
            n_perturbations: Number of perturbed samples to generate.
            pct_words_masked: Percentage of words to mask during perturbation.
            span_length: Average length of spans to mask.
            seed: Random seed.
            device: 'cpu' or 'cuda'. If None, detects automatically.
        """
        self._base_model_name = base_model_name
        self._perturbation_model_name = perturbation_model_name
        self.n_perturbations = n_perturbations
        self.pct_words_masked = pct_words_masked
        self.span_length = span_length
        self.seed = seed

        self.device = device # Resolved lazily

        # Lazy loaded models
        self.base_model = None
        self.base_tokenizer = None
        self.perturb_model = None
        self.perturb_tokenizer = None

    @property
    def name(self) -> str:
        return "detectgpt"

    @property
    def dtype(self) -> str:
        return "text"

    def check_dependencies(self) -> None:
        try:
            import transformers
            import torch
        except ImportError:
            raise ImportError(
                "DetectGPT signal requires 'transformers' and 'torch'. "
                "Please install them via `pip install transformers torch`."
            )

    def _load_models(self):
        if self.base_model is not None:
            return

        self.check_dependencies()
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM

        if not self.device:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Load Base Model (for scoring)
        self.base_tokenizer = AutoTokenizer.from_pretrained(self._base_model_name)
        self.base_model = AutoModelForCausalLM.from_pretrained(self._base_model_name).to(self.device)
        self.base_model.eval()

        # Load Perturbation Model (T5)
        self.perturb_tokenizer = AutoTokenizer.from_pretrained(self._perturbation_model_name)
        self.perturb_model = AutoModelForSeq2SeqLM.from_pretrained(self._perturbation_model_name).to(self.device)
        self.perturb_model.eval()

    def _get_ll(self, text: str) -> float:
        """Computes the log-likelihood of a text under the base model."""
        import torch
        import torch.nn.functional as F
        with torch.no_grad():
            tokenized = self.base_tokenizer(text, return_tensors="pt").to(self.device)
            labels = tokenized.input_ids
            outputs = self.base_model(**tokenized, labels=labels)
            loss = outputs.loss
            # loss is -log(P(x)) averaged over tokens.
            # We assume cross entropy loss which is average NLL.
            return -loss.item()

    def _perturb_text_flan(self, text: str) -> List[str]:
        """
        Uses FLAN-T5 to paraphrase. Much simpler implementation.
        """
        prompt = f"Paraphrase the following text:\n{text}"
        input_ids = self.perturb_tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)

        perturbations = []
        for _ in range(self.n_perturbations):
            outputs = self.perturb_model.generate(
                input_ids,
                do_sample=True,
                max_length=len(text.split()) * 2, # Allow some expansion
                top_p=0.9,
                temperature=0.8 + (np.random.rand() * 0.2) # vary temp slightly
            )
            p_text = self.perturb_tokenizer.decode(outputs[0], skip_special_tokens=True)
            perturbations.append(p_text)

        return perturbations

    def run(self, input_data: str) -> DetectionResult:
        if not input_data or not isinstance(input_data, str):
            return DetectionResult(score=0.0, confidence=0.0, error="Invalid input")

        self._load_models()

        # 1. Calculate unperturbed Log Likelihood
        original_ll = self._get_ll(input_data)

        # 2. Generate perturbations
        perturbations = self._perturb_text_flan(input_data)

        # 3. Calculate perturbed Log Likelihoods
        perturbed_lls = []
        for p_text in perturbations:
            if not p_text.strip():
                continue
            ll = self._get_ll(p_text)
            perturbed_lls.append(ll)

        if not perturbed_lls:
            return DetectionResult(score=0.0, confidence=0.0, error="Failed to generate valid perturbations")

        mu_p = np.mean(perturbed_lls)
        std_p = np.std(perturbed_lls) if len(perturbed_lls) > 1 else 1.0

        # Raw curvature
        curvature = original_ll - mu_p

        # Z-score (Normalized)
        z_score = curvature / (std_p + 1e-8)

        # Convert to native python floats
        if isinstance(z_score, (np.generic, np.ndarray)):
            z_score = float(z_score)

        # Convert z-score to probability [0, 1]
        try:
            if math.isnan(z_score):
                prob = 0.5
            else:
                prob = 1.0 / (1.0 + math.exp(-z_score))
        except OverflowError:
            prob = 1.0 if z_score > 0 else 0.0

        if math.isnan(prob):
            prob = 0.5

        # Calculate confidence from measurement uncertainty
        # Lower std of perturbations = more stable measurement = higher confidence
        # Normalize std_p relative to typical range of log-likelihoods
        # Typical std_p ranges from ~0.1 to ~2.0
        if std_p < 0.2:
            confidence = 0.9  # Very stable perturbations
        elif std_p < 0.5:
            confidence = 0.8  # Stable perturbations
        elif std_p < 1.0:
            confidence = 0.7  # Moderate stability
        elif std_p < 2.0:
            confidence = 0.5  # Lower stability
        else:
            confidence = 0.3  # High variance, low confidence
        
        # Boost confidence if we have many successful perturbations
        if len(perturbed_lls) >= 15:
            confidence = min(confidence + 0.05, 0.95)

        return DetectionResult(
            score=prob,
            confidence=confidence,
            metadata={
                "original_ll": float(original_ll),
                "perturbed_mean_ll": float(mu_p),
                "perturbed_std_ll": float(std_p),
                "curvature": float(curvature),
                "z_score": float(z_score),
                "n_perturbations": len(perturbed_lls)
            }
        )

# Update the default to a model that works with the simple 'paraphrase' prompt logic
# or ensure we document it.
DetectGPTSignal.__init__.__defaults__ = (
    "gpt2-medium",
    "google/flan-t5-small", # Use FLAN for instruction following
    15,
    0.3,
    2,
    42,
    None
)
