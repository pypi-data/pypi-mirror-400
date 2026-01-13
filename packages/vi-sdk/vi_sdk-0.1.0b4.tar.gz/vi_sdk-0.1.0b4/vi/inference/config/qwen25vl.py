#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   qwen25vl.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK Qwen2.5 VL generation config module.
"""

from msgspec import field
from vi.inference.config.base_config import ViGenerationConfig


class Qwen25VLGenerationConfig(ViGenerationConfig):
    """Qwen2.5 VL generation configuration.

    Attributes:
        temperature: Sampling temperature.
        top_k: Top-k sampling.
        top_p: Nucleus sampling probability.
        repetition_penalty: Repetition penalty.
        max_new_tokens: Maximum number of tokens to generate.
        do_sample: Whether to use sampling.
        seed: Random seed for reproducibility. Defaults to 0 for deterministic output.
            Set to -1 to disable seeding and use random generation.
        bos_token_id: Beginning of sentence token id.
        pad_token_id: Padding token id.
        eos_token_id: End of sentence token ids.
        logits_processor: Logits processor.

    """

    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95
    repetition_penalty: float = 1.05
    max_new_tokens: int = 1024
    do_sample: bool = False
    bos_token_id: int = 151643
    pad_token_id: int = 151643
    eos_token_id: list[int] = field(default_factory=lambda: [151645, 151643])
