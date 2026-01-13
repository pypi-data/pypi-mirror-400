#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   conditional_processor.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Conditional XGrammar logits processor for structured output generation.
"""

from enum import Enum, auto
from typing import Any

import torch
import xgrammar as xgr
from vi.inference.logits_processors.debug_processor import apply_xgrammar_on_cpu
from vi.inference.utils.compiler import compile_grammar_str


class COTState(Enum):
    """State machine states for enforced COT generation."""

    FORCE_THINK_OPEN = auto()  # Force <think> at start
    FREE_THINKING = auto()  # Free generation until </think>
    FORCE_ANSWER_OPEN = auto()  # Force <answer> after </think>
    GRAMMAR_ACTIVE = auto()  # JSON schema + </answer>
    COMPLETED = auto()  # Done


class ConditionalXGrammarLogitsProcessor:
    """A logits processor that enforces COT format with <think> and <answer> tags.

    This processor enforces the following output structure:
        <think>...free-form reasoning...</think><answer>STRICT_JSON</answer>

    State machine:
        1. FORCE_THINK_OPEN: Force <think> token(s) at the start
        2. FREE_THINKING: Allow free generation until </think> is produced
        3. FORCE_ANSWER_OPEN: Force <answer> token(s) after </think>
        4. GRAMMAR_ACTIVE: Apply JSON schema grammar + force </answer> at end
        5. COMPLETED: Generation complete

    Attributes:
        xgr_processor: The underlying xgrammar logits processor for JSON schema.
        tokenizer: The tokenizer used for tag encoding/decoding.
        state: Current state in the COT generation state machine.

    """

    @classmethod
    def from_compiled_grammar(
        cls,
        compiled_grammar: "xgr.CompiledGrammar",
        tokenizer: Any,
        suffix_string: str | None = None,
    ) -> "ConditionalXGrammarLogitsProcessor":
        """Construct from a compiled grammar.

        Args:
            compiled_grammar: An xgrammar CompiledGrammar object for JSON schema.
            tokenizer: The tokenizer instance.
            suffix_string: Optional string required after the answer section.
                Defaults to "</answer>" if not specified.

        Returns:
            Configured processor ready for use.

        """
        # Default suffix to </answer> for COT mode
        if suffix_string is None:
            suffix_string = "</answer>"

        # Modify grammar to include suffix
        schema_rules = str(compiled_grammar.grammar)
        updated_schema_rules = schema_rules.replace("root ::=", "schema_rules ::=")
        new_rules = f"""
            root ::= schema_rules ws answer_suffix
            ws ::= [ \\n\\t]*
            answer_suffix ::= "{suffix_string}"
            {updated_schema_rules}
        """
        new_compiled = compile_grammar_str(tokenizer, new_rules)
        base_xgr_processor = xgr.contrib.hf.LogitsProcessor(new_compiled)

        return cls(base_xgr_processor, tokenizer)

    def __init__(self, xgr_processor: Any, tokenizer: Any):
        """Initialize the conditional logits processor.

        Args:
            xgr_processor: The base xgrammar logits processor (with </answer> suffix).
            tokenizer: Tokenizer used for tag encoding/decoding.

        """
        self.xgr_processor: Any = xgr_processor
        self.tokenizer: Any = tokenizer
        self.state: COTState = COTState.FORCE_THINK_OPEN

        # Pre-encode tags
        self.think_open_tag: str = "<think>"
        self.think_close_tag: str = "</think>"
        self.answer_open_tag: str = "<answer>"

        self.think_open_ids: list[int] = self.tokenizer.encode(
            self.think_open_tag, add_special_tokens=False
        )
        self.think_close_ids: list[int] = self.tokenizer.encode(
            self.think_close_tag, add_special_tokens=False
        )
        self.answer_open_ids: list[int] = self.tokenizer.encode(
            self.answer_open_tag, add_special_tokens=False
        )

        # Track position in forced sequences
        self._force_position: int = 0
        self._initial_len: int = 0

    def _force_token(
        self,
        scores: "torch.FloatTensor",
        token_id: int,
    ) -> "torch.FloatTensor":
        """Force a specific token by setting all other logits to -inf.

        Args:
            scores: Logits tensor (shape [batch, vocab_size]).
            token_id: The token ID to force.

        Returns:
            Modified scores with only the target token allowed.

        """
        mask = torch.full_like(scores, float("-inf"))
        mask[:, token_id] = scores[:, token_id]
        return mask

    def _check_tag_in_recent_tokens(
        self,
        input_ids: "torch.LongTensor",
        tag_ids: list[int],
        tag_string: str,
        lookback: int = 50,
    ) -> bool:
        """Check if a tag appears in recent tokens.

        Args:
            input_ids: Tensor of input token IDs (shape [batch, seq_len]).
            tag_ids: List of token IDs for the target tag.
            tag_string: The original tag string for text-based fallback.
            lookback: Number of recent tokens to examine.

        Returns:
            True if the tag is detected.

        """
        if input_ids.shape[1] < len(tag_ids):
            return False

        start_idx = max(0, input_ids.shape[1] - lookback)
        recent_tokens = input_ids[0, start_idx:].tolist()

        # Token-based check
        for i in range(len(recent_tokens) - len(tag_ids) + 1):
            if recent_tokens[i : i + len(tag_ids)] == tag_ids:
                return True

        # Text-based fallback
        try:
            decoded_text = self.tokenizer.decode(
                input_ids[0, start_idx:], skip_special_tokens=False
            )
            if tag_string in decoded_text:
                return True
        except Exception:
            pass

        return False

    def __call__(
        self,
        input_ids: "torch.LongTensor",
        scores: "torch.FloatTensor",
    ) -> "torch.FloatTensor":
        """Apply enforced COT constraints based on current state.

        Enforces the format: <think>...</think><answer>JSON</answer>

        Args:
            input_ids: Input token IDs (shape [1, seq_len]).
            scores: Scores/logits (shape [1, vocab_size]).

        Returns:
            Constrained scores based on current COT state.

        """
        # Initialize on first call
        if self._initial_len == 0:
            self._initial_len = input_ids.shape[1]

        # State: Force <think> at the start
        if self.state == COTState.FORCE_THINK_OPEN:
            if self._force_position < len(self.think_open_ids):
                token_to_force = self.think_open_ids[self._force_position]
                self._force_position += 1
                return self._force_token(scores, token_to_force)
            # All <think> tokens forced, move to free thinking
            self.state = COTState.FREE_THINKING
            self._force_position = 0

        # State: Free thinking until </think>
        if self.state == COTState.FREE_THINKING:
            if self._check_tag_in_recent_tokens(
                input_ids, self.think_close_ids, self.think_close_tag
            ):
                self.state = COTState.FORCE_ANSWER_OPEN
                self._force_position = 0
            return scores  # Free generation

        # State: Force <answer> after </think>
        if self.state == COTState.FORCE_ANSWER_OPEN:
            if self._force_position < len(self.answer_open_ids):
                token_to_force = self.answer_open_ids[self._force_position]
                self._force_position += 1
                return self._force_token(scores, token_to_force)
            # All <answer> tokens forced, activate grammar
            self.state = COTState.GRAMMAR_ACTIVE

        # State: Grammar active (JSON schema + </answer>)
        if self.state == COTState.GRAMMAR_ACTIVE:
            try:
                return apply_xgrammar_on_cpu(self.xgr_processor, input_ids, scores)
            except Exception:
                self.state = COTState.COMPLETED
                return scores

        return scores

    def reset(self) -> None:
        """Reset the processor state for a new generation."""
        self.state = COTState.FORCE_THINK_OPEN
        self._force_position = 0
        self._initial_len = 0
        if hasattr(self.xgr_processor, "reset"):
            self.xgr_processor.reset()
