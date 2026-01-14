# Attribution

A Python library for attributing contributions of context sources in Retrieval-Augmented Generation (RAG) systems.

## Installation

```bash
pip install attribution
```

## Features

- **LLM-Based Citation**: Explicit citations during LLM generation using DSPy
- **Embedding-Based Citation**: Post-processing attribution via semantic similarity
- **Profit Share Calculation**: Weighted citation aggregation for fair attribution

## Quick Start

### Embedding-Based Attribution

```python
from attribution import run_embedding_attribution_pipeline

# Your LLM response (without citations)
response = "The capital of France is Paris. It is known for the Eiffel Tower."

# Context sources with their indices
context = {
    1: "Paris is the capital and largest city of France.",
    2: "The Eiffel Tower is a famous landmark in Paris.",
}

# Map node indices to server/source names
node_map = {
    1: "wikipedia",
    2: "travel_guide",
}

# Run the pipeline
result = run_embedding_attribution_pipeline(
    response_text=response,
    context=context,
    node_map=node_map,
)

print(result["cited_response"])  # Response with <cite:X>...</cite> tags
print(result["stats"])           # Citation statistics per server
print(result["profit_share"])    # Normalized contribution scores
```

### LLM-Based Attribution

```python
from attribution import run_llm_attribution_pipeline

# Pre-generated response with citation tags
cited_response = "<cite:[1]>Paris is the capital of France.</cite> <cite:[2]>The Eiffel Tower is iconic.</cite>"

# Map node indices to server names
node_map = {
    1: "wikipedia",
    2: "travel_guide",
}

result = run_llm_attribution_pipeline(
    generated_response=cited_response,
    node_map=node_map,
)

print(result["profit_share"])
```

### Constructing Citation Prompts

```python
from attribution import construct_citation_prompt

prompt = construct_citation_prompt(
    query="What is the capital of France?",
    context={
        1: "Paris is the capital of France.",
        2: "France is a country in Europe.",
    }
)
```

## API Reference

### Core Functions

- `aggregate_server_citations(llm_response, node_to_server_map)`: Parse citations and count per server
- `calculate_contribution(stats, k_multi=1.5, k_single=1.0)`: Calculate normalized profit shares

### LLM-Based Citation

- `construct_citation_prompt(query, context)`: Build DSPy prompt for citation generation
- `run_llm_attribution_pipeline(generated_response, node_map, ...)`: Full LLM attribution pipeline

### Embedding-Based Citation

- `auto_cite_response(response, context, server_map, ...)`: Add citations using embeddings
- `run_embedding_attribution_pipeline(response_text, context, node_map, ...)`: Full embedding pipeline

## Configuration

### Embedding-Based Settings

- `DEFAULT_EMBEDDING_MODEL`: `'BAAI/bge-small-en-v1.5'`
- `DEFAULT_SIMILARITY_THRESHOLD`: `0.75`
- `DEFAULT_N_GRAM_SIZE`: `5`

### Profit Share Weights

- `k_multi`: Weight for multi-source citations (default: 1.5)
- `k_single`: Weight for single-source citations (default: 1.0)

## License

MIT License - see [LICENSE](LICENSE) for details.
