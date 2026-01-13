import numpy as np
from typing import Dict, List, Union

def calculate_auc(y_true: List[int], y_scores: List[float]) -> float:
    """
    Calculates Area Under the ROC Curve (AUROC) manually.
    """
    if len(set(y_true)) < 2:
        return 0.5  # Undefined if only one class is present

    # Combine and sort by score descending
    desc_score_indices = np.argsort(y_scores)[::-1]
    y_score_sorted = np.array(y_scores)[desc_score_indices]
    y_true_sorted = np.array(y_true)[desc_score_indices]

    # Calculate TPR and FPR
    distinct_value_indices = np.where(np.diff(y_score_sorted))[0]
    threshold_idxs = np.r_[distinct_value_indices, len(y_true_sorted) - 1]

    tps = np.cumsum(y_true_sorted)[threshold_idxs]
    fps = (1 + threshold_idxs) - tps

    # Add (0, 0) point
    tps = np.r_[0, tps]
    fps = np.r_[0, fps]

    if fps[-1] <= 0 or tps[-1] <= 0:
        return 0.5

    fpr = fps / fps[-1]
    tpr = tps / tps[-1]

    # Trapezoidal rule
    try:
        return np.trapz(tpr, fpr)
    except AttributeError:
        # For numpy 2.0+
        return np.trapezoid(tpr, fpr)

def calculate_metrics(y_true: List[int], y_pred_scores: List[float], threshold: float = 0.5) -> Dict[str, float]:
    """
    Calculates standard evaluation metrics.

    Args:
        y_true: List of ground truth labels (0=Human, 1=AI).
        y_pred_scores: List of predicted probabilities [0.0, 1.0].
        threshold: Classification threshold for accuracy/f1.

    Returns:
        Dictionary containing accuracy, precision, recall, f1, and auroc.
    """
    y_true = np.array(y_true)
    y_scores = np.array(y_pred_scores)
    y_pred = (y_scores >= threshold).astype(int)

    tp = np.sum((y_pred == 1) & (y_true == 1))
    tn = np.sum((y_pred == 0) & (y_true == 0))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    auroc = calculate_auc(y_true.tolist(), y_scores.tolist())

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "auroc": float(auroc)
    }
