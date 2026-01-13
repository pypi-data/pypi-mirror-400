"""
Compliance Scanner Use Case

This file contains the ComplianceScanner class implementation from docs/use_cases.md
Use case: Companies ensuring customer-facing content complies with AI disclosure requirements.

Source: docs/use_cases.md (lines 299-338)
"""

from veridex.text import PerplexitySignal
from veridex.image import FrequencySignal


class ComplianceScanner:
    """Enterprise content compliance scanner for AI disclosure requirements"""
    
    def __init__(self, threshold=0.7):
        self.text_detector = PerplexitySignal()
        self.image_detector = FrequencySignal()
        self.threshold = threshold
    
    def scan_marketing_content(self, content):
        """
        Scan marketing content for AI disclosure compliance
        
        Args:
            content: Dict containing 'text', 'images', and 'ai_disclosure' keys
            
        Returns:
            dict: Compliance report with violations list
        """
        violations = []
        
        # Check text
        text_result = self.text_detector.run(content['text'])
        if text_result.score > self.threshold:
            if not content.get('ai_disclosure'):
                violations.append({
                    'type': 'MISSING_AI_DISCLOSURE',
                    'element': 'text',
                    'ai_probability': text_result.score
                })
        
        # Check images
        for img in content.get('images', []):
            img_result = self.image_detector.run(img['path'])
            if img_result.score > self.threshold:
                if not img.get('ai_disclosure'):
                    violations.append({
                        'type': 'MISSING_AI_DISCLOSURE',
                        'element': f"image:{img['path']}",
                        'ai_probability': img_result.score
                    })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'requires_action': len(violations) > 0
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Compliance Scanner Use Case Example")
    print("=" * 60)
    
    # Usage example
    scanner = ComplianceScanner(threshold=0.7)
    
    sample_content = {
        'text': """
        Discover our revolutionary new product that transforms your daily routine
        with cutting-edge technology and innovative features...
        """,
        'ai_disclosure': False,  # No disclosure provided
        # Note: For images, provide actual file paths with disclosure info
        # 'images': [
        #     {'path': 'product_image.png', 'ai_disclosure': False}
        # ]
    }
    
    try:
        result = scanner.scan_marketing_content(sample_content)
        
        print(f"\nCompliance Status: {'✓ COMPLIANT' if result['compliant'] else '✗ NON-COMPLIANT'}")
        print(f"Violations Found: {len(result['violations'])}")
        
        if result['violations']:
            print("\nViolations:")
            for violation in result['violations']:
                print(f"  - {violation['type']}")
                print(f"    Element: {violation['element']}")
                print(f"    AI Probability: {violation['ai_probability']:.2%}")
        
        if result['requires_action']:
            print("\n⚠️  ACTION REQUIRED: Add AI disclosure to flagged content")
    except Exception as e:
        print(f"Error: {e}")
