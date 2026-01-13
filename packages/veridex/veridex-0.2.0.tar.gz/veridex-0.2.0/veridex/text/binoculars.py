from typing import Any
from veridex.core.signal import BaseSignal, DetectionResult

class BinocularsSignal(BaseSignal):
    """
    Implements the 'Binoculars' Zero-Shot Detection method.

    This advanced detection strategy compares the perplexity of two models forms a ratio:
    an 'Observer' model and a 'Performer' model.

    Formula:
        Score = log(PPL_Observer) / log(PPL_Performer)

    Interpretation:
        If the score is below a certain threshold (typically ~0.90), the text is considered
        AI-generated. This method is considered state-of-the-art for zero-shot detection.

    References:
        "Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text" (arXiv:2401.12070)

    Attributes:
        name (str): 'binoculars'
        dtype (str): 'text'
    """

    def __init__(self, observer_id: str = "tiiuae/falcon-7b-instruct", performer_id: str = "tiiuae/falcon-7b", use_mock: bool = False):
        """
        Initialize the Binoculars signal.

        Args:
            observer_id (str): HuggingFace ID for the observer model.
            performer_id (str): HuggingFace ID for the performer model.
            use_mock (bool): If True, returns dummy results without loading models (for testing).
        """
        self.observer_id = observer_id
        self.performer_id = performer_id
        self.use_mock = use_mock
        self._observer_model = None
        self._performer_model = None
        self._tokenizer = None

    @property
    def name(self) -> str:
        return "binoculars"

    @property
    def dtype(self) -> str:
        return "text"

    def check_dependencies(self) -> None:
        if self.use_mock:
            return

        try:
            import torch
            import transformers
        except ImportError:
            raise ImportError(
                "The 'text' extra dependencies (transformers, torch) are required for BinocularsSignal. "
                "Install them with `pip install veridex[text]`."
            )

    def _load_models(self):
        if self.use_mock:
            return

        if self._observer_model is not None and self._performer_model is not None:
            return

        self.check_dependencies()

        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        self._device = device

        # Shared tokenizer usually works if models are from same family
        self._tokenizer = AutoTokenizer.from_pretrained(self.observer_id)

        self._observer_model = AutoModelForCausalLM.from_pretrained(
            self.observer_id,
            trust_remote_code=True,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)

        self._performer_model = AutoModelForCausalLM.from_pretrained(
            self.performer_id,
            trust_remote_code=True,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)

    def _calculate_ppl(self, model, text):
        import torch
        inputs = self._tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            return torch.exp(outputs.loss).item()

    def run(self, input_data: Any) -> DetectionResult:
        if not isinstance(input_data, str):
            return DetectionResult(score=0.0, confidence=0.0, metadata={}, error="Input must be a string.")

        if self.use_mock:
            # Mock behavior for testing without heavy downloads
            # Return a dummy result
            return DetectionResult(
                score=0.9,
                confidence=1.0,
                metadata={
                    "binoculars_score": 0.85,
                    "threshold": 0.90,
                    "mode": "mock"
                }
            )

        try:
            self._load_models()
            import numpy as np

            ppl_observer = self._calculate_ppl(self._observer_model, input_data)
            ppl_performer = self._calculate_ppl(self._performer_model, input_data)

            # Binoculars Score = log(PPL_Observer) / log(PPL_Performer)
            # Avoid division by zero
            if ppl_performer <= 1.0:
                ppl_performer = 1.0001

            score_val = np.log(ppl_observer) / np.log(ppl_performer)

            # Thresholding (from paper, typically around 0.9017 for Falcon)
            # If score < threshold, it is AI.
            threshold = 0.9017

            # Convert to probability:
            # If score is much lower than threshold -> High AI prob.
            # If score is higher than threshold -> Low AI prob.

            is_ai = score_val < threshold
            ai_prob = 0.9 if is_ai else 0.1

            # Calculate confidence from distance to threshold
            # Scores far from threshold indicate high confidence
            dist_from_threshold = abs(score_val - threshold)
            # Typical binoculars scores range from ~0.7 to ~1.1
            # Distance > 0.1 from threshold is very confident
            if dist_from_threshold > 0.15:
                confidence = 0.95
            elif dist_from_threshold > 0.1:
                confidence = 0.88
            elif dist_from_threshold > 0.05:
                confidence = 0.78
            elif dist_from_threshold > 0.02:
                confidence = 0.65
            else:
                confidence = 0.50  # Very close to threshold, uncertain

            return DetectionResult(
                score=ai_prob,
                confidence=confidence,
                metadata={
                    "binoculars_score": score_val,
                    "ppl_observer": ppl_observer,
                    "ppl_performer": ppl_performer,
                    "threshold": threshold,
                    "distance_from_threshold": dist_from_threshold
                }
            )

        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                metadata={},
                error=f"Binoculars failed: {str(e)}"
            )
