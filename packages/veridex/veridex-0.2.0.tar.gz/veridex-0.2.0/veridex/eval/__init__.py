from veridex.eval.dataset import EvaluationDataset, EvaluationSample
from veridex.eval.metrics import calculate_metrics
from veridex.eval.runner import Evaluator

def evaluate_signal(signal, data_list, threshold=0.5):
    """
    Helper function to quickly evaluate a signal on a list of (data, label) tuples.
    """
    dataset = EvaluationDataset.from_list(data_list)
    runner = Evaluator()
    return runner.evaluate(signal, dataset, threshold)
