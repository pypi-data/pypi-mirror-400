"""
Video Deepfake Detection Example
================================
This script demonstrates how to use Veridex to detect deepfakes in video files
using three distinct signals:
1. rPPG (Heartbeat) Analysis
2. Spatiotemporal (I3D) Analysis
3. Lip-Sync (AV Dissonance) Analysis

Usage:
    python video_detection_example.py --input path/to/video.mp4
"""

import argparse
import sys
from typing import Dict, Any

try:
    from veridex.video import RPPGSignal, I3DSignal, LipSyncSignal
except ImportError:
    print("Error: veridex[video] not installed. Please run: pip install veridex[video]")
    sys.exit(1)

def analyze_video(video_path: str) -> None:
    print(f"\n🔍 Analyzing video: {video_path}")
    print("-" * 50)

    # 1. Biological Signal (Heartbeat)
    print("\n[1/3] Running rPPG Signal (Biological Analysis)...")
    rppg = RPPGSignal()
    try:
        r1 = rppg.run(video_path)
        print(f"   > AI Probability: {r1.score:.4f}")
        print(f"   > Confidence:     {r1.confidence:.2f}")
        if r1.metadata:
            print(f"   > SNR:            {r1.metadata.get('snr', 0):.2f}")
    except Exception as e:
        print(f"   > Error: {e}")

    # 2. Spatiotemporal Signal (Motion/Consistency)
    print("\n[2/3] Running I3D Signal (Spatiotemporal Analysis)...")
    i3d = I3DSignal()
    try:
        r2 = i3d.run(video_path)
        print(f"   > AI Probability: {r2.score:.4f}")
        print(f"   > Confidence:     {r2.confidence:.2f}")
    except Exception as e:
        print(f"   > Error: {e}")

    # 3. Lip-Sync Signal (Dubbing)
    print("\n[3/3] Running LipSync Signal (Audio-Visual Sync)...")
    lipsync = LipSyncSignal()
    try:
        r3 = lipsync.run(video_path)
        print(f"   > AI Probability: {r3.score:.4f}")
        print(f"   > Confidence:     {r3.confidence:.2f}")
        if r3.metadata:
            print(f"   > AV Distance:    {r3.metadata.get('av_distance', 0):.4f}")
    except Exception as e:
        print(f"   > Error: {e}")

    print("-" * 50)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Veridex Video Deepfake Detection")
    parser.add_argument("--input", type=str, required=True, help="Path to input video file")

    args = parser.parse_args()
    analyze_video(args.input)
