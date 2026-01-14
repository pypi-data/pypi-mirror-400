"""Citation methods for RAG attribution.

This module provides two approaches for attributing LLM responses to sources:
- LLM-based: Explicit citations during generation
- Embedding-based: Post-processing via semantic similarity
"""

from attribution.citation_methods.llm_based_citation import (
    GenerateAnswerWithCitations,
    construct_citation_prompt,
    run_llm_attribution_pipeline,
)
from attribution.citation_methods.embedding_based_citation import (
    auto_cite_response,
    run_embedding_attribution_pipeline,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_N_GRAM_SIZE,
)

__all__ = [
    # LLM-based citation
    "GenerateAnswerWithCitations",
    "construct_citation_prompt",
    "run_llm_attribution_pipeline",
    # Embedding-based citation
    "auto_cite_response",
    "run_embedding_attribution_pipeline",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_N_GRAM_SIZE",
]
