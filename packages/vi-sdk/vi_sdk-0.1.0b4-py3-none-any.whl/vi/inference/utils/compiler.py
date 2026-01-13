#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   compiler.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK compiler module.
"""

import re
from typing import TYPE_CHECKING, Any

import xgrammar as xgr
from pydantic import BaseModel

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizer

# Patterns to match whitespace rules and eliminate them entirely
# This forces compact JSON output without any whitespace between tokens
_WS_UNBOUNDED_PATTERN = re.compile(r"(ws\s*::=\s*\[[^\]]+\])\*")
_WS_BOUNDED_PATTERN = re.compile(r"(ws\s*::=\s*\[[^\]]+\])\?")

# More aggressive patterns to catch various whitespace rule formats
_WS_ANY_NAME_PATTERN = re.compile(
    r"([\w-]*ws[\w-]*)\s*::=\s*\[[^\]]*\\n[^\]]*\][\*\?]?", re.IGNORECASE
)
_NEWLINE_IN_CHARSET_PATTERN = re.compile(r"(\[[^\]]*)(\\n)([^\]]*\])")


def _get_vocab_size(tokenizer: Any) -> int:
    """Get the actual vocabulary size from a tokenizer.

    Takes the maximum of full vocab and config vocab size to handle
    tokenizers with added tokens.

    Args:
        tokenizer: HuggingFace tokenizer instance.

    Returns:
        The actual vocabulary size to use for grammar compilation.

    """
    full_vocab_size = len(tokenizer.get_vocab())
    config_vocab_size = tokenizer.vocab_size
    return max(full_vocab_size, config_vocab_size)


def _create_compiler(tokenizer: Any) -> "xgr.GrammarCompiler":
    """Create an xgrammar compiler from a tokenizer.

    Args:
        tokenizer: HuggingFace tokenizer instance.

    Returns:
        Configured GrammarCompiler instance.

    """
    vocab_size = _get_vocab_size(tokenizer)
    tokenizer_info = xgr.TokenizerInfo.from_huggingface(
        tokenizer, vocab_size=vocab_size
    )
    return xgr.GrammarCompiler(tokenizer_info, max_threads=8)


def _strip_whitespace_from_grammar(grammar_str: str) -> str:
    r"""Remove whitespace rules from grammar to force compact JSON output.

    Replaces whitespace rules like:
    - ws ::= [...]* -> ws ::= ""
    - ws ::= [...]? -> ws ::= ""
    - Any rule containing \\n in a character class

    This ensures the model generates compact JSON without any extra whitespace
    between tokens, preventing token limit issues.

    Args:
        grammar_str: The grammar string to modify.

    Returns:
        Modified grammar string with whitespace rules eliminated.

    """
    modified = grammar_str

    # Step 1: Replace unbounded ws with bounded, then eliminate
    modified = _WS_UNBOUNDED_PATTERN.sub(r"\1?", modified)
    modified = _WS_BOUNDED_PATTERN.sub(r'ws ::= ""', modified)
    modified = _WS_UNBOUNDED_PATTERN.sub(r'ws ::= ""', modified)

    # Step 2: Find all whitespace-related rules and replace them with empty string
    # This catches rules like: basic-ws, basic-escape-ws, etc.
    lines = modified.split("\n")
    processed_lines = []
    for line in lines:
        stripped = line.strip()
        # Check if this is a whitespace rule definition containing newlines
        if _WS_ANY_NAME_PATTERN.match(stripped):
            # Extract the rule name and replace with empty
            rule_name = stripped.split("::=")[0].strip()
            processed_lines.append(f'{rule_name} ::= ""')
        else:
            processed_lines.append(line)
    modified = "\n".join(processed_lines)

    # Step 3: Remove \n from character classes in remaining rules
    # This is a safety net for inline whitespace patterns
    modified = _NEWLINE_IN_CHARSET_PATTERN.sub(r"\1\3", modified)

    return modified


def _compile_with_compact_whitespace(
    compiler: "xgr.GrammarCompiler",
    schema: type[BaseModel],
) -> "xgr.CompiledGrammar":
    """Compile a schema and strip whitespace rules for compact output.

    Args:
        compiler: An xgrammar GrammarCompiler instance.
        schema: Pydantic BaseModel representing the schema to enforce.

    Returns:
        CompiledGrammar with whitespace rules eliminated.

    """
    initial_grammar = compiler.compile_json_schema(schema)
    grammar_str = str(initial_grammar.grammar)
    compact_grammar_str = _strip_whitespace_from_grammar(grammar_str)

    if compact_grammar_str != grammar_str:
        return compiler.compile_grammar(compact_grammar_str)

    return initial_grammar


def compile_bounded_grammar(
    compiler: "xgr.GrammarCompiler",
    schema: type[BaseModel],
) -> "xgr.CompiledGrammar":
    """Compile a JSON schema grammar with no whitespace allowed.

    Compiles the schema using the provided compiler, then modifies the grammar
    to eliminate all whitespace rules (ws ::= ""). This forces compact JSON
    output and prevents excessive whitespace generation that can hit token limits.

    Args:
        compiler: An xgrammar GrammarCompiler instance.
        schema: Pydantic BaseModel representing the schema to enforce.

    Returns:
        CompiledGrammar: An xgrammar CompiledGrammar with no whitespace allowed.

    """
    return _compile_with_compact_whitespace(compiler, schema)


def compile_grammar_str(
    tokenizer: "PreTrainedTokenizer",
    grammar_str: str,
) -> "xgr.CompiledGrammar":
    """Compile a custom grammar string into an xgrammar compiled grammar.

    This function takes a tokenizer and a grammar definition string, maps the
    vocabulary, and compiles the grammar for use in constrained decoding.

    Args:
        tokenizer: HuggingFace tokenizer instance.
        grammar_str: Grammar definition string in xgrammar syntax.

    Returns:
        CompiledGrammar: An xgrammar CompiledGrammar object usable for
        constrained decoding.

    """
    compiler = _create_compiler(tokenizer)
    return compiler.compile_grammar(grammar_str)
