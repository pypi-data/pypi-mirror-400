# Attention Is All You Need

*Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Google Research, Google Brain, All You, Attention Is*

---

## Executive Summary

This paper addresses the limitations of recurrent (RNN) and convolutional (CNN) neural networks in sequence transduction tasks like machine translation. Existing models struggled with long-range dependencies and suffered from inherently sequential computation, which prevented full parallelization during training and significantly increased training time. The need for a more efficient and powerful architecture that could capture complex relationships in sequential data without these computational bottlenecks was a critical challenge in the field.

The key innovation is the Transformer architecture, a novel model that relies entirely on attention mechanisms, completely eliminating recurrence and convolutions. The Transformer uses an encoder-decoder structure where each layer consists of multi-head self-attention and position-wise feed-forward networks. The core mechanism, scaled dot-product attention (Attention(Q, K, V) = softmax(QKT/√dk)V), allows the model to directly relate all positions in a sequence, capturing dependencies regardless of their distance. This design enables constant-time operations for relating distant positions and superior parallelizability, as each output element can be computed independently.

The Transformer achieves state-of-the-art results on major machine translation benchmarks. On the WMT 2014 English-to-German task, it attains a BLEU score of 28.4, improving over the previous best by more than 2 BLEU. For English-to-French translation, it reaches 41.8 BLEU with significantly lower training costs, requiring only 3.5 days on 8 GPUs. The model demonstrates remarkable training efficiency, reaching state-of-the-art performance in just 12 hours on eight P100 GPUs. Furthermore, the architecture generalizes effectively to other tasks, achieving strong results on English constituency parsing with both large and limited training data.

The significance of this work is profound, as the Transformer architecture has become the dominant model not only in machine translation but across the entire field of natural language processing and beyond. Its superior performance, combined with its high parallelizability and training efficiency, has enabled the development of much larger and more powerful models. The attention-only paradigm has fundamentally shifted the research direction away from recurrence and convolution, paving the way for modern large language models like BERT and GPT. This paper's influence extends to computer vision, speech processing, and other domains, establishing attention as a foundational building block in deep learning.

---

## Key Findings

- The Transformer architecture, based solely on attention mechanisms, outperforms existing complex recurrent or convolutional models in machine translation tasks.
- The proposed model achieves a new state-of-the-art BLEU score of 28.4 on WMT 2014 English-to-German translation, improving over the best existing results by over 2 BLEU.
- On the WMT 2014 English-to-French translation task, the model achieves a state-of-the-art 41.8 BLEU score with significantly lower training costs (3.5 days on 8 GPUs).
- The Transformer architecture demonstrates superior parallelizability and requires significantly less training time compared to previous models.
- The model generalizes well to other tasks, achieving successful results on English constituency parsing with both large and limited training data.

---

## Methodology

The authors propose the Transformer, a novel network architecture that relies entirely on attention mechanisms, completely eliminating recurrence and convolutions. The model consists of an encoder and decoder connected through attention mechanisms. Experiments were conducted on two machine translation tasks (WMT 2014 English-to-German and English-to-French) and English constituency parsing to evaluate performance, training efficiency, and generalization capabilities.

---

## Technical Details

### Architecture

- **Name**: Transformer
- **Type**: Encoder-decoder
- **Core Mechanism**: Self-attention
- **Encoder Layers**: 6
- **Decoder Layers**: 6
- **Model Dimension**: 512
- **Feed Forward Dimension**: 2048
- **Attention Heads**: Not specified in provided text
- **Sub-layers**: 
  - Multi-head self-attention
  - Position-wise feed-forward network
- **Residual Connections**: True
- **Layer Normalization**: True
- **Position Encoding**: Not detailed in provided sections

### Attention Mechanism

- **Type**: Scaled Dot-Product Attention
- **Formula**: Attention(Q, K, V) = softmax(QKT/√dk)V
- **Scaling Factor**: 1/√dk
- **Multi-head**: True
- **Parallel Computation**: True

### Feed Forward Network

- **Formula**: FFN(x) = max(0, xW1 + b1)W2 + b2
- **Activation**: ReLU
- **Input/Output Dim**: 512
- **Inner Layer Dim**: 2048

### Key Innovations

- Elimination of recurrence and convolution
- Reliance entirely on attention mechanisms
- Constant number of operations to relate distant positions
- Superior parallelizability

---

## Results

### Machine Translation

**WMT 2014 English-to-German**
- BLEU Score: 28.4
- Improvement: Over 2 BLEU over previous best

**WMT 2014 English-to-French**
- BLEU Score: 41.8
- Training Time: 3.5 days on 8 GPUs
- Cost: Significantly lower training costs

### Training

- Time to State-of-the-Art: 12 hours on eight P100 GPUs
- Parallelization: Significantly more parallelizable than RNNs

### Generalization

**English Constituency Parsing**
- Performance: Successful results
- Data Efficiency: Works with both large and limited training data

---

## Contributions

- Introduction of the Transformer architecture, a new simple network architecture based solely on attention mechanisms that dispenses with recurrence and convolutions entirely.
- Demonstration that attention-only models can achieve superior performance in machine translation tasks while being more parallelizable and requiring significantly less training time.
- Establishment of new state-of-the-art results on major machine translation benchmarks.
- Proof of the Transformer's strong generalization capabilities by successfully applying it to English constituency parsing tasks.

---

### Quick Facts

| Metric | Value |
|--------|-------|
| Quality Score | 9/10 |
| References | 40 citations |
| Best BLEU (En-De) | 28.4 |
| Best BLEU (En-Fr) | 41.8 |
| Training Time (SOTA) | 12 hours |
| Architecture Type | Encoder-Decoder |
| Core Innovation | Self-Attention Only |
