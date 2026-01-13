"""
Forensic Analyzer Use Case

This file contains the ForensicAnalyzer class implementation from docs/use_cases.md
Use case: Law firms identifying AI-generated documents in discovery processes.

Source: docs/use_cases.md (lines 239-287)
"""

from veridex.text import BinocularsSignal, PerplexitySignal
import pandas as pd


class ForensicAnalyzer:
    """Legal and forensic document analysis for discovery"""
    
    def __init__(self):
        self.detector_high_accuracy = BinocularsSignal(observer_id="distilgpt2", performer_id="gpt2")
        self.detector_fast = PerplexitySignal()
    
    def analyze_document_batch(self, documents):
        """
        Analyze a batch of documents for AI generation probability
        
        Args:
            documents: List of dicts containing 'id', 'filename', 'text', 'created_at'
            
        Returns:
            pd.DataFrame: Analysis results with flagged documents
        """
        results = []
        
        for doc in documents:
            # Quick scan first
            quick_result = self.detector_fast.run(doc['text'])
            
            # If flagged, run detailed analysis
            if quick_result.score > 0.6:
                detailed_result = self.detector_high_accuracy.run(doc['text'])
                
                results.append({
                    'document_id': doc['id'],
                    'filename': doc['filename'],
                    'ai_probability': detailed_result.score,
                    'confidence': detailed_result.confidence,
                    'flagged': detailed_result.score > 0.75,
                    'timestamp': doc.get('created_at'),
                    'metadata': detailed_result.metadata
                })
            else:
                results.append({
                    'document_id': doc['id'],
                    'filename': doc['filename'],
                    'ai_probability': quick_result.score,
                    'flagged': False
                })
        
        return pd.DataFrame(results)
    
    def generate_report(self, results_df):
        """Generate summary report from analysis results"""
        return {
            'total_documents': len(results_df),
            'flagged_documents': len(results_df[results_df['flagged']]),
            'avg_ai_probability': results_df['ai_probability'].mean(),
            'high_confidence_flags': len(results_df[
                (results_df['flagged']) & (results_df['confidence'] > 0.8)
            ])
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Forensic Analyzer Use Case Example")
    print("=" * 60)
    
    # Usage example
    analyzer = ForensicAnalyzer()
    
    # Sample documents
    sample_documents = [
        {
            'id': 'doc_001',
            'filename': 'contract_draft.txt',
            'text': 'This agreement is entered into by and between...',
            'created_at': '2024-01-15'
        },
        {
            'id': 'doc_002',
            'filename': 'memo.txt',
            'text': 'The utilization of artificial intelligence in contemporary business...',
            'created_at': '2024-02-20'
        }
    ]
    
    try:
        # Analyze batch
        results_df = analyzer.analyze_document_batch(sample_documents)
        print("\nAnalysis Results:")
        print(results_df.to_string())
        
        # Generate report
        report = analyzer.generate_report(results_df)
        print("\n\nSummary Report:")
        print(f"Total Documents: {report['total_documents']}")
        print(f"Flagged Documents: {report['flagged_documents']}")
        print(f"Average AI Probability: {report['avg_ai_probability']:.2%}")
        print(f"High Confidence Flags: {report['high_confidence_flags']}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This example requires pandas and BinocularsSignal dependencies.")
