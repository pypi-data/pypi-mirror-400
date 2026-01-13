"""
Content Moderator Use Case

This file contains the ContentModerator class implementation from docs/use_cases.md
Use case: Social media platforms and online communities identifying AI-generated content.

Source: docs/use_cases.md (lines 21-63)
"""

from veridex.text import PerplexitySignal, StylometricSignal
from veridex.image import FrequencySignal


class ContentModerator:
    """Content moderation for social media platforms"""
    
    def __init__(self):
        self.text_detector = PerplexitySignal()
        self.image_detector = FrequencySignal()
    
    def moderate_post(self, post):
        """
        Moderate a social media post containing text and/or images
        
        Args:
            post: Dict containing 'text' and/or 'images' keys
            
        Returns:
            str: Moderation decision ('FLAG_FOR_REVIEW' or 'PASS')
        """
        results = {}
        
        # Check text content
        if post.get('text'):
            text_result = self.text_detector.run(post['text'])
            results['text'] = {
                'ai_probability': text_result.score,
                'confidence': text_result.confidence
            }
        
        # Check images
        if post.get('images'):
            image_results = []
            for img_path in post['images']:
                img_result = self.image_detector.run(img_path)
                image_results.append(img_result.score)
            results['images'] = {
                'avg_ai_probability': sum(image_results) / len(image_results)
            }
        
        # Apply moderation rules
        if results.get('text', {}).get('ai_probability', 0) > 0.8:
            return "FLAG_FOR_REVIEW"
        
        return "PASS"


if __name__ == "__main__":
    print("=" * 60)
    print("Content Moderator Use Case Example")
    print("=" * 60)
    
    # Usage example
    moderator = ContentModerator()
    
    # Example post
    sample_post = {
        'text': "Check this amazing AI-written content...",
        # Note: For images, provide actual paths
        # 'images': ['image1.png', 'image2.png']
    }
    
    try:
        decision = moderator.moderate_post(sample_post)
        print(f"\nModeration Decision: {decision}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nBest Practices:")
    print("- ✓ Use multiple signals for robust detection")
    print("- ✓ Set appropriate thresholds for your platform")
    print("- ✓ Always allow human review for flagged content")
    print("- ✓ Log decisions for auditing")
