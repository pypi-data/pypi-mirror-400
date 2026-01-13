from typing import Any
import math
from veridex.core.signal import BaseSignal, DetectionResult

class PerplexitySignal(BaseSignal):
    """
    Detects AI content using Perplexity and Burstiness metrics.

    This signal uses a pre-trained causal language model (default: GPT-2) to calculate
    the perplexity (surprise) of the text.

    Metrics:
        - Perplexity: Exponential of the average negative log-likelihood per token.
          Lower perplexity indicates the text is more predictable to the model (likely AI).
        - Burstiness: The standard deviation of perplexity across sentences.
          AI text tends to have consistent perplexity (low burstiness), while human writing varies.

    Dependencies:
        Requires `transformers`, `torch`, and optionally `nltk` for sentence splitting.

    Attributes:
        name (str): 'perplexity_burstiness'
        dtype (str): 'text'
        model_id (str): HuggingFace model identifier.
    """

    def __init__(self, model_id: str = "gpt2"):
        """
        Initialize the Perplexity signal.

        Args:
            model_id (str): The HuggingFace model ID to use for calculation.
                            Defaults to 'gpt2' (fast, reasonable baseline).
        """
        self.model_id = model_id
        self._model = None
        self._tokenizer = None

    @property
    def name(self) -> str:
        return "perplexity_burstiness"

    @property
    def dtype(self) -> str:
        return "text"

    def check_dependencies(self) -> None:
        try:
            import torch
            import transformers
        except ImportError:
            raise ImportError(
                "The 'text' extra dependencies (transformers, torch) are required for PerplexitySignal. "
                "Install them with `pip install veridex[text]`."
            )

    def _load_model(self):
        if self._model is not None:
            return

        self.check_dependencies()

        # Local import to avoid top-level dependency
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        # Use CPU by default for broader compatibility in this context
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"

        self._device = device
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self._model = AutoModelForCausalLM.from_pretrained(self.model_id).to(device)

    def _split_sentences(self, text: str) -> list[str]:
        try:
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            return nltk.sent_tokenize(text)
        except ImportError:
            # Fallback to simple splitting if nltk is not available
            import re
            return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

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
                metadata={},
                error="Input string is empty."
            )

        try:
            self._load_model()
        except ImportError as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                metadata={},
                error=str(e)
            )
        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                metadata={},
                error=f"Failed to load model '{self.model_id}': {e}"
            )

        import torch
        import numpy as np

        try:
            sentences = self._split_sentences(input_data)
            # If no sentences found (e.g. empty or weird text), treat whole text as one
            if not sentences:
                sentences = [input_data]

            perplexities = []

            for sentence in sentences:
                # Skip empty sentences
                if not sentence.strip():
                    continue

                inputs = self._tokenizer(sentence, return_tensors="pt")
                inputs = {k: v.to(self._device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self._model(**inputs, labels=inputs["input_ids"])
                    loss = outputs.loss
                    ppl = torch.exp(loss).item()
                    perplexities.append(ppl)

            if not perplexities:
                 return DetectionResult(
                    score=0.0,
                    confidence=0.0,
                    metadata={},
                    error="Could not calculate perplexity for any sentence."
                )

            mean_perplexity = float(np.mean(perplexities))
            burstiness = float(np.std(perplexities)) if len(perplexities) > 1 else 0.0

            # Heuristic Scoring (Experimental)
            # Research suggests AI text has lower perplexity and lower burstiness.
            # We define a simple probability mapping.
            # Note: Thresholds are arbitrary and need calibration on real datasets.
            # GPT-2 Output approx: PPL ~ 10-20. Human: PPL ~ 40-100+.

            # Simple logistic-like decay for score based on PPL
            # If PPL is low (<30), probability of AI is high.
            # If PPL is high (>80), probability of AI is low.

            # We use a threshold of 50 for perplexity as a midpoint.
            ppl_score = 1.0 / (1.0 + math.exp((mean_perplexity - 50) / 10))

            # Burstiness acts as a modifier? Or just a separate signal?
            # For now, let's keep the score based mainly on Perplexity but return both metrics.
            # AI = Low Burstiness.

            return DetectionResult(
                score=ppl_score,
                confidence=0.6, # Moderate confidence as this is a heuristic
                metadata={
                    "mean_perplexity": mean_perplexity,
                    "burstiness": burstiness,
                    "sentence_count": len(sentences),
                    "model_id": self.model_id
                }
            )

        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                metadata={},
                error=f"Error calculating perplexity/burstiness: {e}"
            )
