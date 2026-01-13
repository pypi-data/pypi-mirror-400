# Audio Detection Concepts

AI-generated audio (deepfakes) has improved significantly, but often lacks the natural imperfections of human speech.

## Spectral Analysis

**SpectralSignal** analyzes the frequency spectrum for artifacts. Synthetic audio might lack high-frequency details or have unnatural spectral continuity.

## Physiological Signs (Breathing)

**BreathingSignal** looks for natural breathing pauses. Deepfake models often generate continuous speech without the natural pauses humans need to breathe, or they insert them in unnatural places.

## Foundation Models (Wav2Vec, AASIST)

Using large pre-trained models like Wav2Vec or specialized architectures like AASIST (for anti-spoofing) allows detecting subtle patterns learned from massive datasets of real and spoofed audio.
