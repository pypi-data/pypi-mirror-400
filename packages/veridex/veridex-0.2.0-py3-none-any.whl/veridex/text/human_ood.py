
import numpy as np
import torch
from typing import Optional
from veridex.core.signal import BaseSignal, DetectionResult
from scipy.special import expit

class HumanOODSignal(BaseSignal):
    """
    Implements a zero-shot "Human Texts Are Outliers" (HumanOOD) detection signal.

    This signal treats the LLM's own generations as the "In-Distribution" (ID) class
    and human texts as outliers (OOD).

    It generates N samples from the model to form an ID cluster, then computes the
    Mahalanobis or Euclidean distance of the input text's embedding from this cluster.

    Higher distance = More likely to be Human (Outlier).
    Lower distance = More likely to be Machine (ID).

    Result score is 1.0 - (normalized_distance), so that AI (Low distance) -> 1.0.
    """

    def __init__(
        self,
        model_name: str = "gpt2-medium",
        n_samples: int = 20,
        max_length: int = 128,
        distance_metric: str = "euclidean",
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.n_samples = n_samples
        self.max_length = max_length
        self.distance_metric = distance_metric
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')

        self.model = None
        self.tokenizer = None

    @property
    def name(self) -> str:
        return "human_ood"

    @property
    def dtype(self) -> str:
        return "text"

    def check_dependencies(self) -> None:
        try:
            import transformers
            import torch
            import scipy
        except ImportError:
            raise ImportError(
                "HumanOODSignal requires 'transformers', 'torch', and 'scipy'."
            )

    def _load_models(self):
        if self.model is not None:
            return
        self.check_dependencies()
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def _get_embedding(self, text: str) -> np.ndarray:
        """Computes the mean hidden state embedding for the text."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            # Use the last hidden state
            hidden_states = outputs.hidden_states[-1] # (batch, seq, dim)
            # Mean pooling over sequence
            # Mask out padding tokens if any (not critical for single sample gen but good practice)
            mask = inputs.attention_mask.unsqueeze(-1) # (batch, seq, 1)
            sum_embeddings = torch.sum(hidden_states * mask, dim=1)
            sum_mask = torch.clamp(mask.sum(dim=1), min=1e-9)
            mean_embedding = sum_embeddings / sum_mask

        return mean_embedding.cpu().numpy()[0]

    def run(self, input_data: str) -> DetectionResult:
        if not input_data or not isinstance(input_data, str):
            return DetectionResult(score=0.0, confidence=0.0, error="Invalid input")

        self._load_models()

        # 1. Get embedding of input text
        input_emb = self._get_embedding(input_data)

        # 2. Generate N samples from the model (ID distribution)
        # We prompt with the first few tokens of input to condition the style,
        # or use unconditional generation?
        # If we use unconditional, the cluster is "generic English".
        # If we use conditional, we check if the input *continuation* matches the model's *continuation*.
        # The paper suggests "machine-generated texts are in-distribution".
        # If we just generate random text, the distribution is huge.
        # Let's generate completions based on the prefix of the input (first 5 tokens).

        tokens = self.tokenizer.encode(input_data)
        prefix_len = min(5, len(tokens))
        prefix_ids = torch.tensor([tokens[:prefix_len]]).to(self.device)

        generated_embs = []

        for _ in range(self.n_samples):
            with torch.no_grad():
                output_ids = self.model.generate(
                    prefix_ids,
                    do_sample=True,
                    max_length=min(len(tokens) + 20, self.max_length), # Generate similar length
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                gen_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
                generated_embs.append(self._get_embedding(gen_text))

        generated_embs = np.array(generated_embs)

        # 3. Compute Distance
        # We calculate the distance of input_emb to the distribution of generated_embs.
        # Ideally Mahalanobis, but requires n_samples > dim.
        # GPT2 dim is 768 or 1024. n_samples 20 is too small.
        # Fallback: Euclidean distance to centroid.

        centroid = np.mean(generated_embs, axis=0)

        if self.distance_metric == "euclidean":
            # Distance from input to centroid
            dist = np.linalg.norm(input_emb - centroid)

            # We also need to know the typical spread (radius) of the cluster to normalize.
            # Average distance of samples to centroid.
            radii = np.linalg.norm(generated_embs - centroid, axis=1)
            avg_radius = np.mean(radii)
            std_radius = np.std(radii)

            # Z-score of the distance?
            # if dist >> avg_radius, it is outlier (Human).
            z_dist = (dist - avg_radius) / (std_radius + 1e-8)

            # If z_dist is high (positive), it's far -> Human.
            # If z_dist is low (near 0 or negative), it's close -> Machine.

            # Map z-score to probability of being AI.
            # AI = Low distance.
            # P(AI) = 1 - P(Human)
            # P(Human) is related to CDF(z_dist).

            # Using sigmoid (-z_dist) so that high z (Human) gives low score.
            score = expit(-z_dist) # Numerically stable version of 1 / (1 + exp(z_dist))

        else:
            return DetectionResult(score=0.0, confidence=0.0, error="Unsupported metric")

        return DetectionResult(
            score=float(score),
            confidence=0.7, # Lower confidence as this is a zero-shot approx
            metadata={
                "distance": float(dist),
                "avg_radius": float(avg_radius),
                "z_dist": float(z_dist),
                "n_samples": self.n_samples
            }
        )
