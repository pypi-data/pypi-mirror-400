"""
Shared utilities for search functionality across context modes.
"""


def format_search_prompt(question: str, results: str) -> str:
    """Format a question and search results into a prompt for the LLM."""
    return f"Relevant context:\n{results}\n\n{question}"

