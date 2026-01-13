# Video Signals

Video deepfake detection analyzes temporal patterns, biological signals, and audio-visual synchronization to identify synthetic content.

## Overview

Veridex provides three specialized video detection signals:

- **RPPGSignal**: Detects biological heartbeat patterns in facial video
- **I3DSignal**: Analyzes spatiotemporal motion features
- **LipSyncSignal**: Checks audio-visual synchronization
- **VideoEnsemble**: Combines all three with confidence-weighted fusion

## Core Concepts

### Biological Analysis (RPPG)

Remote photoplethysmography (rPPG) extracts heartbeat signals from subtle color changes in facial skin. Deepfakes often lack these biological rhythms.

**Strengths**: Hard to fake biological signals  
**Limitations**: Requires clear faces, good lighting

### Spatiotemporal Analysis (I3D)

Inception-3D networks learn motion patterns across space and time. Synthetic videos exhibit different temporal statistics than real ones.

**Strengths**: Works on full frames, doesn't need faces  
**Limitations**: Requires minimum 64 frames

### Audio-Visual Synchronization (LipSync)

SyncNet measures correspondence between audio and lip movements. Poor sync indicates dubbing or voice cloning.

**Strengths**: Effective for audio manipulation  
**Limitations**: Needs both audio and video

## Ensemble Approach

The `VideoEnsemble` combines all three signals using weighted averaging, where more confident signals have higher influence.

### Benefits

- **Robust**: Works even if some signals fail
- **Confident**: Higher accuracy through fusion
- **Transparent**: Shows individual signal results

## Usage

See the [Video Detection Guide](../tutorials/video_detection.md) for detailed usage examples.

## Technical Details

- **Face Detection**: MediaPipe (preferred) or Haar Cascades (fallback)
- **Model Weights**: Currently using placeholder URLs (requires real weights)
- **Performance**: ~5-8 FPS on CPU, 5-10x faster on GPU

## Research

Based on:
- PhysNet (Yu et al., 2019) for rPPG
- Inception-I3D (Carreira & Zisserman, 2017) for motion
- SyncNet (Chung & Zisserman, 2016) for lip-sync
