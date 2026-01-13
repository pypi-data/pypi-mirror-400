#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   nvila.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NVILA generation config module.
"""

from vi.inference.config.base_config import ViGenerationConfig


class NVILAGenerationConfig(ViGenerationConfig):
    """NVILA generation configuration.

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
        eos_token_id: End of sentence token id.
        logits_processor: Logits processor.

    """

    temperature: float = 1
    top_k: int = 50
    top_p: float = 1
    repetition_penalty: float = 1.05
    max_new_tokens: int = 1024
    do_sample: bool = False
    bos_token_id: int = 151643
    pad_token_id: int = 151643
    eos_token_id: int = 151645
