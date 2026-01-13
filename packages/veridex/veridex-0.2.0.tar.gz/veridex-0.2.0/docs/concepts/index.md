# Concepts Overview

Veridex operates on a **Signal-based Architecture**. Instead of a single monolithic model, it uses a collection of independent "Signals" that analyze different aspects of the content.

## What is a Signal?

A `Signal` is an independent detector that focuses on a specific feature or artifact of AI generation. For example:
- **PerplexitySignal**: Checks if the text is "too predictable" (low perplexity), which is common in LLMs.
- **FrequencySignal**: Checks for artifacts in the frequency domain of an image.

## Why Probabilistic?

AI detection is inherently uncertain. Veridex returns a `score` (probability of being AI) and a `confidence` (how sure the signal is about that score). This allows for better decision-making and aggregation.

## Modalities

Veridex supports:
- **Text**: analyzing linguistic patterns, entropy, and embeddings.
- **Image**: analyzing pixel statistics, frequency artifacts, and semantic consistency.
- **Audio**: analyzing spectral features, breathing patterns, and using foundation models.
