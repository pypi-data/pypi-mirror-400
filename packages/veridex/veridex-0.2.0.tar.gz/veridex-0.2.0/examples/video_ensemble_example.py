"""
Video Deepfake Detection Example using VideoEnsemble

This example demonstrates how to use the VideoEnsemble class to combine
multiple video detection signals (RPPG, I3D, LipSync) for robust detection.

Requirements:
    pip install veridex[video]
    
Optional (recommended for better face detection):
    Already included in video dependencies since your update

Usage:
    python examples/video_ensemble_example.py path/to/video.mp4
"""

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Detect deepfakes in videos using ensemble of signals"
    )
    parser.add_argument("video_path", type=str, help="Path to video file")
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Show individual signal details"
    )
    
    args = parser.parse_args()
    
    # Validate input
    video_path = Path(args.video_path)
    if not video_path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    print(f"\n🎬 Analyzing Video: {video_path.name}")
    print("=" * 70)
    
    try:
        from veridex.video import VideoEnsemble
        
        # Create ensemble detector (combines RPPG, I3D, LipSync)
        ensemble = VideoEnsemble()
        
        # Run detection
        print("\n⏳ Running ensemble detection (this may take a minute)...\n")
        result = ensemble.run(str(video_path))
        
        # Display results
        print("\n" + "=" * 70)
        print("📊 DETECTION RESULTS")
        print("=" * 70)
        
        # Overall score
        ai_label = "🤖 AI-GENERATED" if result.score > 0.6 else "👤 LIKELY REAL"
        confidence_bar = "▰" * int(result.confidence * 10) + "▱" * (10 - int(result.confidence * 10))
        
        print(f"\n{ai_label}")
        print(f"  AI Probability:  {result.score:.2%}")
        print(f"  Confidence:      {confidence_bar} ({result.confidence:.2%})")
        
        # Metadata
        if 'num_successful' in result.metadata:
            success_rate = result.metadata['num_successful'] / result.metadata['num_total']
            print(f"  Signals Used:    {result.metadata['num_successful']}/{result.metadata['num_total']} ({success_rate:.0%})")
        
        # Individual signals (if verbose or only one signal succeeded)
        if args.verbose or result.metadata.get('num_successful', 0) <= 1:
            if 'individual_results' in result.metadata:
                print("\n" + "-" * 70)
                print("📈 INDIVIDUAL SIGNALS:")
                print("-" * 70)
                
                signal_names = {
                    'rppg_physnet': 'rPPG (Biological Heartbeat)',
                    'spatiotemporal_i3d': 'I3D (Motion Analysis)',
                    'lipsync_syncnet': 'LipSync (Audio-Visual)'
                }
                
                for sig_name, sig_result in result.metadata['individual_results'].items():
                    display_name = signal_names.get(sig_name, sig_name)
                    score = sig_result['score']
                    conf = sig_result['confidence']
                    
                    print(f"\n  {display_name}:")
                    print(f"    Score:       {score:.2%}")
                    print(f"    Confidence:  {conf:.2%}")
                    
                    # Additional metadata
                    if 'metadata' in sig_result and sig_result['metadata']:
                        for key, value in sig_result['metadata'].items():
                            if key != 'signal_name':
                                print(f"    {key.replace('_', ' ').title()}: {value}")
        
        # Warnings/Notes
        if result.error:
            print(f"\n⚠️  Error: {result.error}")
        
        if result.confidence < 0.5:
            print("\n⚠️  Note: Low confidence. Consider multiple detection runs or manual review.")
        
        print("\n" + "=" * 70)
        
        # Interpretation guide
        print("\n💡 INTERPRETATION:")
        print("   • Score > 0.7:  Strong AI signal")
        print("   • Score 0.4-0.7: Uncertain (inconclusive)")
        print("   • Score < 0.4:  Likely authentic")
        print("   • Confidence matters! Low confidence = unreliable prediction")
        
        print("\n" + "=" * 70 + "\n")
        
    except ImportError as e:
        print(f"\n❌ Missing dependencies: {e}")
        print("   Install with: pip install veridex[video]")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Detection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
