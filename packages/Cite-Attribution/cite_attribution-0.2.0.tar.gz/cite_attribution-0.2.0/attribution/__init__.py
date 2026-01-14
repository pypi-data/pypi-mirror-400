"""Attribution library for RAG systems.

A library for attributing contributions of context sources in
Retrieval-Augmented Generation (RAG) systems.
"""

from attribution.utils import aggregate_server_citations, calculate_contribution
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

__version__ = "0.1.0"
__author__ = "Your Name"

__all__ = [
    # Core utilities
    "aggregate_server_citations",
    "calculate_contribution",
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
