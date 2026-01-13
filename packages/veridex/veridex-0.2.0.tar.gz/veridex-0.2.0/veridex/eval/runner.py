from typing import Dict, List, Any
import time
from tqdm import tqdm
from veridex.core.signal import BaseSignal
from veridex.eval.dataset import EvaluationDataset
from veridex.eval.metrics import calculate_metrics

class Evaluator:
    """
    Runs evaluation for a given signal and dataset.
    """

    def __init__(self):
        pass

    def evaluate(self, signal: BaseSignal, dataset: EvaluationDataset, threshold: float = 0.5) -> Dict[str, Any]:
        """
        Runs the signal on the dataset and computes metrics.

        Args:
            signal: The detection signal to evaluate.
            dataset: The dataset containing samples.
            threshold: Threshold for binary classification metrics.

        Returns:
            Dictionary with metrics and detailed results.
        """
        if signal.dtype == 'text':
             # Check if we need to filter dataset or if we assume user passes correct dataset
             # For now, we trust the user passes appropriate data.
             pass

        y_true = []
        y_scores = []
        results = []

        errors = 0

        start_time = time.time()

        for sample in tqdm(dataset, desc=f"Evaluating {signal.name}"):
            try:
                result = signal.run(sample.data)

                if result.error:
                    errors += 1
                    # Treat error as 0.5 score or skip?
                    # Usually skipping is safer for pure metric calculation,
                    # but we should note the failure rate.
                    # For this implementation, we will SKIP samples that error out for metric calc.
                    results.append({
                        "data": str(sample.data)[:50] + "...", # Truncate for log
                        "label": sample.label,
                        "score": None,
                        "error": result.error
                    })
                    continue

                y_true.append(sample.label)
                y_scores.append(result.score)
                results.append({
                    "label": sample.label,
                    "score": result.score,
                    "confidence": result.confidence,
                    "metadata": result.metadata
                })

            except Exception as e:
                errors += 1
                results.append({
                    "data": str(sample.data)[:50] + "...",
                    "label": sample.label,
                    "score": None,
                    "error": str(e)
                })

        end_time = time.time()

        metrics = calculate_metrics(y_true, y_scores, threshold)

        metrics["error_rate"] = errors / len(dataset) if len(dataset) > 0 else 0.0
        metrics["throughput"] = len(dataset) / (end_time - start_time) if (end_time - start_time) > 0 else 0.0

        return {
            "signal_name": signal.name,
            "metrics": metrics,
            "num_samples": len(dataset),
            "num_errors": errors,
            # "detailed_results": results # Optional: might be too large
        }
