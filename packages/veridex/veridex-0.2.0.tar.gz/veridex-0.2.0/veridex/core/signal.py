from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class DetectionResult(BaseModel):
    """
    Standardized output model for all detection signals.

    Attributes:
        score (float): Normalized probability score indicating AI-likelihood.
            Range [0.0, 1.0], where 0.0 is confidently Human and 1.0 is confidently AI.
        confidence (float): A measure of the reliability of the score estimation.
            Range [0.0, 1.0], where 1.0 means the signal is fully confident in its assessment.
            
            Confidence interpretation:
            - 0.0-0.3: Low confidence (heuristics, untrained models, errors)
            - 0.4-0.6: Moderate confidence (statistical methods, limited data)
            - 0.7-0.9: High confidence (trained models with good predictions)
            - 0.9-1.0: Very high confidence (strong model predictions, clear patterns)
            
            For model-based signals, confidence is extracted from model outputs (softmax probabilities,
            margins, etc.). For heuristic signals, confidence reflects empirical reliability.
            
        metadata (Dict[str, Any]): Dictionary containing signal-specific intermediate values,
            features, or debug information used to derive the score.
        error (Optional[str]): Error message if the signal failed to execute.
            If present, `score` and `confidence` should be treated as invalid or default.
    """
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized score indicating AI probability. 0=Human, 1=AI.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Reliability of the score estimation.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional signal-specific information.")
    error: Optional[str] = Field(None, description="Error message if the signal failed to execute.")

class BaseSignal(ABC):
    """
    Abstract base class for all content detection signals.

    A 'Signal' is a specialized detector that analyzes content of a specific type (text, image, audio)
    and produces a probabilistic assessment of whether it is AI-generated.

    Subclasses must implement:
        - `name`: Unique string identifier.
        - `dtype`: Input data type supported.
        - `run()`: The core detection logic.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for the signal.
        
        Returns:
            str: A short, snake_case name (e.g., 'zlib_entropy', 'perplexity').
        """
        pass

    @property
    @abstractmethod
    def dtype(self) -> str:
        """
        Data type this signal operates on.
        
        Returns:
            str: One of 'text', 'image', 'audio'.
        """
        pass

    @abstractmethod
    def run(self, input_data: Any) -> DetectionResult:
        """
        Execute the detection logic on the provided input.

        Args:
            input_data (Any): The content to analyze. Type should match `self.dtype` expectations
                (e.g., str for 'text', path or numpy array for 'image/audio').

        Returns:
            DetectionResult: The result containing score, confidence, and metadata.
        """
        pass

    def check_dependencies(self) -> None:
        """
        Optional hook to check if required heavy dependencies are installed.

        This is called before expensive operations or at initialization time.
        
        Raises:
            ImportError: If required extra dependencies (e.g., torch, transformers) are missing.
        """
        pass
