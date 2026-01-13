# Text Detection Concepts

AI text detection relies on identifying statistical patterns that distinguish model-generated text from human-written text.

## Perplexity and Burstiness

**Perplexity** measures how "surprised" a model is by the text. LLMs tend to generate text with lower perplexity (more predictable) than humans.
**Burstiness** measures the variation in perplexity. Humans tend to write with more variable sentence structures, leading to higher burstiness.

## Zero-Shot Detection

Methods like **DetectGPT** and **Binoculars** use the model itself (or a proxy) to detect its own output without needing training data. They rely on the observation that model-generated text occupies "negative curvature" regions of the model's log-probability function.

## Outlier Detection

**HumanOOD** treats human text as the "in-distribution" data and AI text as outliers. By clustering embeddings of human text, we can detect AI text as being far from the cluster center.
