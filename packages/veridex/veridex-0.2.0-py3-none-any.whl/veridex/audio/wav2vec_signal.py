"""
Wav2Vec 2.0 foundation model detector for audio deepfakes.

Uses self-supervised learning models pre-trained on large speech corpora
and fine-tuned for deepfake detection. Provides robust generalization
to unseen vocoders and high accuracy on ASVspoof benchmarks.
"""

from typing import Any, Union
from pathlib import Path
import numpy as np
from veridex.core.signal import BaseSignal, DetectionResult


class Wav2VecSignal(BaseSignal):
    """
    Audio deepfake detector using Wav2Vec 2.0 foundation models.
    
    Leverages pre-trained models fine-tuned for anti-spoofing to detect synthetic speech.
    Models typically include:
    - nii-yamagishilab/wav2vec-large-anti-deepfake
    - facebook/wav2vec2-base-960h (for feature extraction)
    
    These models provide state-of-the-art accuracy with strong generalization to
    unseen vocoders and TTS systems.

    Note:
        Requires robust hardware (preferably GPU) for reasonable inference speeds.

    Attributes:
        name (str): 'wav2vec_audio_detector'
        dtype (str): 'audio'
        model_id (str): HuggingFace model identifier.
    """
    
    def __init__(
        self,
        model_id: str = "nii-yamagishilab/wav2vec-large-anti-deepfake",
        use_gpu: bool = True,
    ):
        """
        Initialize the Wav2Vec detector.
        
        Args:
            model_id: HuggingFace model identifier or local path
            use_gpu: Use GPU acceleration if available
        """
        self.model_id = model_id
        self.use_gpu = use_gpu
        self._model = None
        self._processor = None
        self._device = None
    
    @property
    def name(self) -> str:
        return "wav2vec_audio_detector"
    
    @property
    def dtype(self) -> str:
        return "audio"
    
    def check_dependencies(self) -> None:
        try:
            import torch
            import transformers
            import librosa
            import soundfile
        except ImportError:
            raise ImportError(
                "Wav2Vec detector requires 'torch', 'transformers', 'librosa', and 'soundfile'. "
                "Install with: pip install veridex[audio]"
            )
    
    def _load_model(self):
        """Lazy load the model."""
        if self._model is not None:
            return
        
        self.check_dependencies()
        
        import torch
        from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
        
        # Determine device
        if self.use_gpu and torch.cuda.is_available():
            self._device = torch.device("cuda")
        else:
            self._device = torch.device("cpu")
        
        try:
            # Load processor and model
            self._processor = Wav2Vec2Processor.from_pretrained(self.model_id)
            self._model = Wav2Vec2ForSequenceClassification.from_pretrained(
                self.model_id
            ).to(self._device)
            self._model.eval()
            
        except Exception as e:
            # Fallback: use base wav2vec for feature extraction
            # and simple classifier (less accurate but works)
            raise ImportError(
                f"Failed to load model '{self.model_id}': {e}\n"
                "The model may not be available. Consider using SpectralSignal instead."
            )
    
    def run(self, input_data: Any) -> DetectionResult:
        """
        Detect AI-generated audio using Wav2Vec 2.0.
        
        Args:
            input_data: Path to audio file (str or Path)
            
        Returns:
            DetectionResult with score, confidence, and model metadata
        """
        if not isinstance(input_data, (str, Path)):
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error="Input must be a file path (str or Path)"
            )
        
        try:
            self._load_model()
        except ImportError as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error=str(e)
            )
        
        try:
            import torch
            from veridex.audio.utils import load_audio, validate_audio
            
            # Load audio at 16kHz (Wav2Vec standard)
            audio, sr = load_audio(input_data, target_sr=16000)
            
            # Validate
            is_valid, error_msg = validate_audio(audio, sr)
            if not is_valid:
                return DetectionResult(
                    score=0.0,
                    confidence=0.0,
                    error=error_msg
                )
            
            # Preprocess audio
            inputs = self._processor(
                audio,
                sampling_rate=sr,
                return_tensors="pt",
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                
                # Get probabilities
                probs = torch.nn.functional.softmax(logits, dim=-1)
                
                # Assuming binary classification: [Real, Fake]
                # Model may use different label orders, check config
                fake_prob = probs[0, 1].item() if probs.shape[1] == 2 else probs[0, 0].item()
            
            # Compute confidence based on margin
            confidence = self._compute_confidence(probs[0].cpu().numpy())
            
            return DetectionResult(
                score=float(fake_prob),
                confidence=confidence,
                metadata={
                    "model_id": self.model_id,
                    "device": str(self._device),
                    "audio_duration": len(audio) / sr,
                    "logits": logits[0].cpu().tolist(),
                }
            )
            
        except Exception as e:
            return DetectionResult(
                score=0.0,
                confidence=0.0,
                error=f"Wav2Vec detection failed: {e}"
            )
    
    def _compute_confidence(self, probs: np.ndarray) -> float:
        """
        Compute confidence based on prediction margin.
        
        Higher margin = more confident prediction.
        """
        # Confidence based on max probability
        max_prob = np.max(probs)
        
        # Also consider the margin to second-best
        sorted_probs = np.sort(probs)[::-1]
        if len(sorted_probs) > 1:
            margin = sorted_probs[0] - sorted_probs[1]
            # Confidence increases with margin
            confidence = 0.5 + 0.5 * margin
        else:
            confidence = max_prob
        
        return float(confidence)
