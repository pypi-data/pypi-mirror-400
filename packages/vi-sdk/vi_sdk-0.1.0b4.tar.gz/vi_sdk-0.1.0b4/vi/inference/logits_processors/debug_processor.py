#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   debug_processor.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Debug wrapper for XGrammar logits processor.
"""

import torch
import xgrammar as xgr
from rich import print as rprint
from transformers import PreTrainedTokenizer


def apply_xgrammar_on_cpu(
    xgr_processor: xgr.contrib.hf.LogitsProcessor,
    input_ids: torch.LongTensor,
    scores: torch.FloatTensor,
) -> torch.FloatTensor:
    """Apply xgrammar processing on CPU and return to original device.

    XGrammar operations are performed on CPU for compatibility, then
    results are moved back to the original device.

    Note:
        This function involves CPU-GPU memory transfers on each call.
        For long generations, this can add latency. The xgrammar library
        currently requires CPU tensors for grammar operations. Future
        versions may support GPU-native processing.

    Args:
        xgr_processor: The xgrammar logits processor.
        input_ids: Token IDs (batch_size, sequence_length).
        scores: Unnormalized logits (batch_size, vocab_size).

    Returns:
        Modified logits on the same device as input scores.

    """
    original_device = scores.device
    original_dtype = scores.dtype

    # Skip transfer if already on CPU
    if original_device.type == "cpu":
        return xgr_processor(input_ids, scores)

    # Transfer to CPU, process, and transfer back
    # Use non_blocking=True to allow async transfers where possible
    input_ids_cpu = input_ids.cpu()
    scores_cpu = scores.cpu()
    modified_scores_cpu = xgr_processor(input_ids_cpu, scores_cpu)
    return modified_scores_cpu.to(device=original_device, dtype=original_dtype)


class DebugXGrammarLogitsProcessor:
    """Debug wrapper for XGrammar logits processor with detailed error diagnostics.

    Wraps the XGrammar LogitsProcessor to provide comprehensive debugging information
    when grammar constraints fail during structured output generation. Displays recent
    tokens, candidate tokens, and decoding context to help diagnose schema violations.

    """

    @classmethod
    def from_compiled_grammar(
        cls,
        compiled_grammar: xgr.CompiledGrammar,
        tokenizer: PreTrainedTokenizer,
    ) -> "DebugXGrammarLogitsProcessor":
        """Create a LogitsProcessor from a compiled grammar and tokenizer."""
        base_xgr_processor = xgr.contrib.hf.LogitsProcessor(compiled_grammar)
        return cls(base_xgr_processor, tokenizer)

    def __init__(
        self,
        xgr_processor: xgr.contrib.hf.LogitsProcessor,
        tokenizer: PreTrainedTokenizer,
    ):
        """Initialize the debug wrapper.

        Args:
            xgr_processor: Base XGrammar logits processor.
            tokenizer: Tokenizer for decoding token IDs for error reporting.

        """
        self._xgr_processor = xgr_processor
        self._tokenizer = tokenizer
        self._call_count = 0

    def __call__(
        self,
        input_ids: torch.LongTensor,
        scores: torch.FloatTensor,
    ) -> torch.FloatTensor:
        """Process logits with grammar constraints and detailed error reporting.

        Args:
            input_ids: Token IDs generated so far (batch_size, sequence_length).
            scores: Unnormalized logits (batch_size, vocab_size).

        Returns:
            Modified logits with invalid grammar productions masked out.

        Raises:
            AssertionError: If XGrammar fails, with detailed diagnostic output.

        """
        self._call_count += 1

        try:
            return apply_xgrammar_on_cpu(self._xgr_processor, input_ids, scores)
        except AssertionError as e:
            self._print_error_diagnostics(e, input_ids, scores)
            raise

    def _print_error_diagnostics(
        self,
        error: AssertionError,
        input_ids: torch.LongTensor,
        scores: torch.FloatTensor,
    ) -> None:
        """Print detailed error diagnostics for debugging."""
        rprint(f"\n=== XGRAMMAR ASSERTION ERROR (Call #{self._call_count}) ===")
        rprint(f"Error: {error}")
        rprint(f"Input IDs shape: {input_ids.shape}")
        rprint(f"Scores shape: {scores.shape}")

        if input_ids.shape[1] > 0:
            recent_tokens = input_ids[0, -10:].tolist()
            rprint(f"Recent tokens: {recent_tokens}")
            recent_text = self._tokenizer.decode(
                recent_tokens, skip_special_tokens=False
            )
            rprint(f"Recent text: {repr(recent_text)}")

        top_token_id = torch.argmax(scores[0]).item()
        top_token_text = self._tokenizer.decode(
            [top_token_id], skip_special_tokens=False
        )
        rprint(f"Top scoring token ID: {top_token_id}")
        rprint(f"Top scoring token text: {repr(top_token_text)}")

        top_5_ids = torch.topk(scores[0], 5).indices.tolist()
        rprint("Top 5 token candidates:")
        for i, token_id in enumerate(top_5_ids):
            token_text = self._tokenizer.decode([token_id], skip_special_tokens=False)
            rprint(f"  {i + 1}. ID {token_id}: {repr(token_text)}")

        rprint("=== END XGRAMMAR ERROR INFO ===\n")
