"""
Dataset Curator Use Case

This file contains the DatasetCurator class implementation from docs/use_cases.md
Use case: Researchers filtering AI-generated samples from datasets and validating data provenance.

Source: docs/use_cases.md (lines 350-390)
"""

from veridex.text import PerplexitySignal
import json


class DatasetCurator:
    """Research dataset curation tool for filtering AI-generated content"""
    
    def __init__(self):
        self.detector = PerplexitySignal()
    
    def curate_text_dataset(self, dataset_path, output_path):
        """
        Curate a text dataset by separating human/AI/uncertain samples
        
        Args:
            dataset_path: Path to input JSON dataset
            output_path: Path to save curated output
            
        Returns:
            dict: Statistics about the curation process
        """
        with open(dataset_path) as f:
            data = json.load(f)
        
        curated = {
            'human_samples': [],
            'ai_samples': [],
            'uncertain_samples': []
        }
        
        for sample in data:
            result = self.detector.run(sample['text'])
            
            sample['veridex_score'] = result.score
            sample['veridex_confidence'] = result.confidence
            
            if result.score < 0.3 and result.confidence > 0.6:
                curated['human_samples'].append(sample)
            elif result.score > 0.7 and result.confidence > 0.6:
                curated['ai_samples'].append(sample)
            else:
                curated['uncertain_samples'].append(sample)
        
        with open(output_path, 'w') as f:
            json.dump(curated, f, indent=2)
        
        return {
            'total': len(data),
            'human': len(curated['human_samples']),
            'ai': len(curated['ai_samples']),
            'uncertain': len(curated['uncertain_samples'])
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Dataset Curator Use Case Example")
    print("=" * 60)
    
    # Usage example - create a sample dataset first
    sample_dataset_path = '/tmp/sample_dataset.json'
    output_path = '/tmp/curated_dataset.json'
    
    # Create sample dataset
    sample_data = [
        {'id': 1, 'text': 'This is a human-written sample with natural flow and variability.'},
        {'id': 2, 'text': 'The implementation of artificial intelligence systems requires careful consideration of ethical implications and societal impacts.'},
        {'id': 3, 'text': 'Hey! Check this out - super cool stuff happening here!'}
    ]
    
    try:
        # Save sample dataset
        with open(sample_dataset_path, 'w') as f:
            json.dump(sample_data, f)
        
        # Curate dataset
        curator = DatasetCurator()
        stats = curator.curate_text_dataset(sample_dataset_path, output_path)
        
        print("\nCuration Statistics:")
        print(f"Total Samples: {stats['total']}")
        print(f"Human Samples: {stats['human']}")
        print(f"AI Samples: {stats['ai']}")
        print(f"Uncertain Samples: {stats['uncertain']}")
        
        print(f"\nCurated dataset saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure you have write permissions to /tmp/")
