"""
Fact Checker Use Case

This file contains the FactChecker class implementation from docs/use_cases.md
Use case: News organizations verifying content authenticity and detecting AI-generated misinformation.

Source: docs/use_cases.md (lines 151-213)
"""

from veridex.text import PerplexitySignal
from veridex.image import FrequencySignal, ELASignal
from veridex.audio import Wav2VecSignal


class FactChecker:
    """Fact-checking system for journalism and news verification"""
    
    def __init__(self):
        self.text_detector = PerplexitySignal()
        self.image_detector_1 = FrequencySignal()
        self.image_detector_2 = ELASignal()
        self.audio_detector = Wav2VecSignal()
    
    def verify_article(self, article):
        """
        Verify an article's content across text, images, and audio
        
        Args:
            article: Dict containing 'id', 'content', 'images', 'audio_clips'
            
        Returns:
            dict: Verification report with findings and risk level
        """
        report = {
            'article_id': article['id'],
            'findings': []
        }
        
        # Analyze text
        text_result = self.text_detector.run(article['content'])
        if text_result.score > 0.7:
            report['findings'].append({
                'type': 'TEXT',
                'concern': 'Potentially AI-generated text',
                'confidence': text_result.confidence,
                'score': text_result.score
            })
        
        # Analyze images (check for manipulation)
        for img_path in article.get('images', []):
            freq_result = self.image_detector_1.run(img_path)
            ela_result = self.image_detector_2.run(img_path)
            
            if freq_result.score > 0.75 or ela_result.score > 0.75:
                report['findings'].append({
                    'type': 'IMAGE',
                    'file': img_path,
                    'concern': 'Potential AI generation or manipulation',
                    'freq_score': freq_result.score,
                    'ela_score': ela_result.score
                })
        
        # Analyze audio/video quotes
        for audio_path in article.get('audio_clips', []):
            audio_result = self.audio_detector.run(audio_path)
            if audio_result.score > 0.8:
                report['findings'].append({
                    'type': 'AUDIO',
                    'file': audio_path,
                    'concern': 'Potential voice deepfake',
                    'score': audio_result.score
                })
        
        report['risk_level'] = self._assess_risk(report['findings'])
        return report
    
    def _assess_risk(self, findings):
        """Assess overall risk level based on findings"""
        if len(findings) >= 3:
            return 'HIGH'
        elif len(findings) >= 1:
            return 'MEDIUM'
        return 'LOW'


if __name__ == "__main__":
    print("=" * 60)
    print("Fact Checker Use Case Example")
    print("=" * 60)
    
    # Usage example
    checker = FactChecker()
    
    sample_article = {
        'id': 'article_001',
        'content': """
        Breaking news: Recent developments in artificial intelligence have shown
        remarkable progress in natural language processing capabilities...
        """,
        # Note: For images and audio, provide actual file paths
        # 'images': ['article_image1.png'],
        # 'audio_clips': ['interview.wav']
    }
    
    try:
        report = checker.verify_article(sample_article)
        
        print(f"\nArticle ID: {report['article_id']}")
        print(f"Risk Level: {report['risk_level']}")
        print(f"Findings: {len(report['findings'])}")
        
        for finding in report['findings']:
            print(f"\n  - Type: {finding['type']}")
            print(f"    Concern: {finding['concern']}")
            if 'score' in finding:
                print(f"    Score: {finding['score']:.2%}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nWorkflow Integration:")
    print("HIGH risk → Senior Editor Review → Additional Verification")
    print("MEDIUM risk → Fact-Checker Review → Additional Verification")
    print("LOW risk → Standard Editorial Process")
