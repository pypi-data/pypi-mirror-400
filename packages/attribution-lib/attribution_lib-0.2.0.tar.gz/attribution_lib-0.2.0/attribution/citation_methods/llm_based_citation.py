"""LLM-Based Citation method for RAG attribution.

In this approach, the LLM itself is responsible for explicit attribution
during the generation phase using a DSPy signature.
"""

import os
from typing import Dict, Any, Optional

import dspy
from dspy.signatures import Signature

from attribution.utils import aggregate_server_citations, calculate_contribution


class GenerateAnswerWithCitations(Signature):
    """
    Generate a concise answer to the query using ONLY the provided sources.
    You MUST wrap every factual phrase, quoted text, or synthesized idea with
    the exact citation format: <cite:[NODE_INDICES]></cite>, where NODE_INDICES
    is a comma-separated list of the source indices (e.g., 1,4,6).
    Every sentence or claim must be inside a <cite> tag.
    Do not include any text outside a <cite> tag.
    """
    sources: str = dspy.InputField(
        desc="Numbered source content (e.g., '1: content 1; 2: content 2')"
    )
    query: str = dspy.InputField()
    answer: str = dspy.OutputField(
        desc="Answer containing only <cite:[indices]>...</cite> tags with an extra summary section and closure section"
    )


def construct_citation_prompt(query: str, context: Dict[int, str]) -> str:
    """
    Constructs the raw prompt string for RAG attribution using DSPy.

    Args:
        query: The user's question.
        context: A dictionary mapping node indices to their content.

    Returns:
        The formatted prompt string ready for an LLM.
    """
    # Format the context dictionary into a numbered string
    sources_str = "\n".join([f"{k}: {v}" for k, v in context.items()])

    # Build the prompt using the signature's docstring as instructions
    instructions = GenerateAnswerWithCitations.__doc__.strip()

    prompt = f"""Instructions:
            {instructions}

            Sources:
            {sources_str}

            Query: {query}

            Answer:"""

    return prompt


def run_llm_attribution_pipeline(
    generated_response: str,
    node_map: Dict[int, str],
    k_multi: float = 1.5,
    k_single: float = 1.0
) -> Dict[str, Any]:
    """
    Run the attribution pipeline on a pre-generated LLM response.

    This version of the pipeline skips generation and focuses on:
    1. Parsing citations from the external response.
    2. Aggregating citation counts per server.
    3. Calculating profit share based on weighted citations.

    Args:
        generated_response: The answer string containing <cite:[indices]> tags.
        node_map: A dictionary mapping node indices to server names.
        k_multi: Weight for multi-source citations.
        k_single: Weight for single-source citations.

    Returns:
        A dictionary containing stats and profit share data.
    """

    # 1. Citation Aggregation
    # This utility parses the <cite> tags from the response string
    try:
        stats = aggregate_server_citations(generated_response, node_map)
    except Exception as e:
        raise ValueError(f"Failed to parse citations from response: {e}")

    # 2. Profit Share Calculation
    # Normalizes the counts into a distribution (0.0 to 1.0)
    profit_share = calculate_contribution(
        stats,
        k_multi=k_multi,
        k_single=k_single
    )

    return {
        "cited_response": generated_response,
        "stats": stats,
        "profit_share": profit_share
    }
