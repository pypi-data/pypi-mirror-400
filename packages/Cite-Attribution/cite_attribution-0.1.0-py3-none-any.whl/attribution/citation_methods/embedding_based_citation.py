"""Embedding-Based Citation method for RAG attribution.

This method performs attribution as a post-processing step using
semantic similarity analysis with embeddings.
"""

import re
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import nltk
from fastembed import TextEmbedding
from sklearn.metrics.pairwise import cosine_similarity

from attribution.utils import aggregate_server_citations, calculate_contribution

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


# Default configuration
DEFAULT_EMBEDDING_MODEL = 'BAAI/bge-small-en-v1.5'
DEFAULT_SIMILARITY_THRESHOLD = 0.75
DEFAULT_N_GRAM_SIZE = 5

# Global model cache
_embedding_model = None


def get_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> TextEmbedding:
    """Get or initialize the embedding model (cached)."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=model_name)
    return _embedding_model


def split_text_into_chunks(text: str, chunk_size: int) -> List[str]:
    """
    Split text into overlapping word n-gram chunks.

    Args:
        text: The input text to split.
        chunk_size: Number of words per chunk.

    Returns:
        A list of text chunks.
    """
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = text.split()
    chunks = []

    if len(words) < chunk_size:
        return [" ".join(words)]

    for i in range(len(words) - chunk_size + 1):
        chunks.append(" ".join(words[i: i + chunk_size]))
    return chunks


def auto_cite_response(
    response: str,
    context: Dict[int, str],
    server_map: Dict[int, str],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    n_gram_size: int = DEFAULT_N_GRAM_SIZE,
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL
) -> str:
    """
    Automatically add citations to a response using embedding similarity.

    This function finds the best source for each response n-gram and builds
    a <cite:nodes> string, preserving original formatting.

    Args:
        response: The LLM-generated response (without citations).
        context: A dictionary mapping node indices to their content.
        server_map: A dictionary mapping node indices to server names.
        similarity_threshold: Minimum cosine similarity for attribution (default: 0.75).
        n_gram_size: Number of words per chunk for comparison (default: 5).
        embedding_model_name: Name of the sentence transformer model to use.

    Returns:
        The response with <cite:node_id>...</cite> tags inserted.
    """
    embedding_model = get_embedding_model(embedding_model_name)

    response_chunks = split_text_into_chunks(response, n_gram_size)
    if not response_chunks:
        return response

    # Flatten context for embedding: (sentence, node_index, server_name)
    source_triples: List[Tuple[str, int, str]] = []
    for node_idx, node_content in context.items():
        server_name = server_map.get(node_idx, "UNKNOWN")
        source_sentences = nltk.sent_tokenize(node_content)
        for sentence in source_sentences:
            source_triples.append((sentence, node_idx, server_name))

    source_chunks = [t[0] for t in source_triples]
    if not source_chunks:
        return response

    # Generate Embeddings and Similarity
    all_texts = response_chunks + source_chunks
    embeddings = np.array(list(embedding_model.embed(all_texts)))

    response_embeddings = embeddings[:len(response_chunks)]
    source_embeddings = embeddings[len(response_chunks):]
    similarity_matrix = cosine_similarity(response_embeddings, source_embeddings)

    # Map Chunk Index -> Best Node Index
    chunk_to_node_map: List[int] = []

    for i in range(len(response_chunks)):
        chunk_sims = similarity_matrix[i]
        best_match_idx = np.argmax(chunk_sims)
        best_similarity = chunk_sims[best_match_idx]

        if best_similarity >= similarity_threshold:
            chunk_to_node_map.append(source_triples[best_match_idx][1])
        else:
            chunk_to_node_map.append(0)

    # Reconstruct with Citations (Preserving Spaces)
    tokens = re.findall(r'(\s+)|([^\s]+)', response)
    original_tokens: List[str] = [t[0] or t[1] for t in tokens]

    word_tokens: List[str] = [t[1] for t in tokens if t[1]]
    sanitized_words = [
        re.sub(r'[^\w]', '', w).lower()
        for w in word_tokens if w and re.match(r'\w+', w)
    ]

    word_to_node_map: List[int] = [0] * len(sanitized_words)

    for chunk_idx, node_id in enumerate(chunk_to_node_map):
        if node_id != 0:
            start_word_idx = chunk_idx
            for offset in range(n_gram_size):
                word_idx = start_word_idx + offset
                if word_idx < len(sanitized_words):
                    word_to_node_map[word_idx] = node_id

    cited_response_parts: List[str] = []
    current_citation_node = 0
    current_cited_segment = ""

    sanitized_word_index = 0

    for token in original_tokens:
        is_word = bool(re.match(r'\w+', token))

        if is_word:
            mapped_node = (
                word_to_node_map[sanitized_word_index]
                if sanitized_word_index < len(word_to_node_map)
                else 0
            )
            sanitized_word_index += 1
        else:
            mapped_node = current_citation_node

        if mapped_node != current_citation_node:
            if current_citation_node != 0:
                cited_response_parts.append(
                    f"<cite:{current_citation_node}>{current_cited_segment}</cite>"
                )
            else:
                cited_response_parts.append(current_cited_segment)

            current_citation_node = mapped_node
            current_cited_segment = token
        else:
            current_cited_segment += token

    # Close the final segment
    if current_citation_node != 0:
        cited_response_parts.append(
            f"<cite:{current_citation_node}>{current_cited_segment}</cite>"
        )
    else:
        cited_response_parts.append(current_cited_segment)

    return "".join(cited_response_parts)


def run_embedding_attribution_pipeline(
    response_text: str,
    context: Dict[int, str],
    node_map: Dict[int, str],
    k_multi: float = 1.5,
    k_single: float = 1.0,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    n_gram_size: int = DEFAULT_N_GRAM_SIZE,
) -> Dict[str, Any]:
    """
    Run the full embedding-based citation pipeline.

    This pipeline:
    1. Generates a clean response using the LLM
    2. Auto-cites the response using embedding similarity
    3. Aggregates citation counts per server
    4. Calculates profit share based on weighted citations

    Args:
        query: The user's question.
        response_text: LLm response
        context: A dictionary mapping node indices to their content.
        node_map: A dictionary mapping node indices to server names.
        k_multi: Weight for multi-source citations (default: 1.5).
        k_single: Weight for single-source citations (default: 1.0).
        similarity_threshold: Minimum cosine similarity for attribution (default: 0.75).
        n_gram_size: Number of words per chunk for comparison (default: 5).
        api_key: Optional API key for the LLM.

    Returns:
        A dictionary containing:
        - 'cited_response': The response with citation tags
        - 'stats': Citation statistics per server
        - 'profit_share': Normalized profit share per server
    """
    # Alignment and Auto-Citation
    cited_response = auto_cite_response(
        response_text, context, node_map,
        similarity_threshold=similarity_threshold,
        n_gram_size=n_gram_size
    )

    # Citation Aggregation
    stats = aggregate_server_citations(cited_response, node_map)

    # Profit Share Calculation
    profit_share = calculate_contribution(
        stats, k_multi=k_multi, k_single=k_single)

    return {
        "cited_response": cited_response,
        "stats": stats,
        "profit_share": profit_share
    }
