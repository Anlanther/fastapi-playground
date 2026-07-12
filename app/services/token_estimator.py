"""Simple token estimator hooks.

This module provides a pluggable estimator function that approximates
token usage for simple accounting. It's intentionally naive (word-based),
and should be replaced with a provider-specific estimator for accurate
counts (e.g., tiktoken or model-specific tokenizer).
"""


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    # rough heuristic: 1 token ~= 0.75 words, use words/0.75
    words = len(text.split())
    return max(1, int(words / 0.75))
