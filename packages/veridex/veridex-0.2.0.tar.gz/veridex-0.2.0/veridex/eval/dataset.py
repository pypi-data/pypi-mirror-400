from typing import Any, List, Tuple, Union, Optional
from pydantic import BaseModel

class EvaluationSample(BaseModel):
    """
    A single sample for evaluation.
    """
    data: Any
    label: int  # 0 for Human, 1 for AI
    metadata: Optional[dict] = None

class EvaluationDataset:
    """
    Manages a collection of samples for evaluation.
    """
    def __init__(self, samples: List[EvaluationSample]):
        self.samples = samples

    @classmethod
    def from_list(cls, data_list: List[Tuple[Any, int]]):
        """
        Creates a dataset from a list of (data, label) tuples.
        """
        samples = [
            EvaluationSample(data=d, label=l)
            for d, l in data_list
        ]
        return cls(samples)

    def __iter__(self):
        return iter(self.samples)

    def __len__(self):
        return len(self.samples)
