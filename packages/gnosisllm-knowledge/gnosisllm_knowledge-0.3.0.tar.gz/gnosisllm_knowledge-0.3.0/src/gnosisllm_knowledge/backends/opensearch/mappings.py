"""OpenSearch index mappings for knowledge documents."""

from __future__ import annotations

from typing import Any

from gnosisllm_knowledge.backends.opensearch.config import OpenSearchConfig


def get_knowledge_index_settings(config: OpenSearchConfig) -> dict[str, Any]:
    """Get index settings for knowledge documents.

    Args:
        config: OpenSearch configuration.

    Returns:
        Index settings dictionary.
    """
    settings: dict[str, Any] = {
        "index": {
            "number_of_shards": config.number_of_shards,
            "number_of_replicas": config.number_of_replicas,
            "refresh_interval": config.refresh_interval,
            "knn": True,
            "knn.algo_param.ef_search": config.knn_algo_param_ef_search,
        }
    }

    # Set default ingest pipeline if configured
    pipeline_name = config.ingest_pipeline_name
    if pipeline_name:
        settings["index"]["default_pipeline"] = pipeline_name

    return settings


def get_knowledge_index_mappings(config: OpenSearchConfig) -> dict[str, Any]:
    """Get index mappings for knowledge documents with k-NN vectors.

    Args:
        config: OpenSearch configuration.

    Returns:
        Index mappings dictionary.
    """
    embedding_field = config.embedding_field  # Default: content_embedding

    return {
        "properties": {
            # === Document Identity ===
            "id": {"type": "keyword"},
            "url": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "standard",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 512}},
            },
            "source": {"type": "keyword"},
            # === Multi-tenant Fields ===
            "account_id": {"type": "keyword"},
            "collection_id": {"type": "keyword"},
            "collection_name": {"type": "keyword"},  # For aggregation display
            "source_id": {"type": "keyword"},
            # === Content ===
            "content": {
                "type": "text",
                "analyzer": "standard",
                "term_vector": "with_positions_offsets",  # For highlighting
            },
            # === Embedding Vector ===
            # Field name matches config.embedding_field (default: content_embedding)
            embedding_field: {
                "type": "knn_vector",
                "dimension": config.embedding_dimension,
                "method": {
                    "name": "hnsw",
                    "space_type": config.knn_space_type,
                    "engine": config.knn_engine,
                    "parameters": {
                        "ef_construction": config.knn_algo_param_ef_construction,
                        "m": config.knn_algo_param_m,
                    },
                },
            },
            # === Chunking Information ===
            "chunk_index": {"type": "integer"},
            "total_chunks": {"type": "integer"},
            "parent_doc_id": {"type": "keyword"},
            "start_position": {"type": "integer"},
            "end_position": {"type": "integer"},
            # === Quality & Validation ===
            "quality_score": {"type": "float"},
            "language": {"type": "keyword"},
            "content_hash": {"type": "keyword"},
            "word_count": {"type": "integer"},
            # === Status ===
            "status": {"type": "keyword"},
            # === PII Handling ===
            "pii_detected": {"type": "boolean"},
            "pii_redacted": {"type": "boolean"},
            # === Metadata ===
            "metadata": {"type": "object", "enabled": True, "dynamic": True},
            # === Timestamps ===
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "indexed_at": {"type": "date"},
        }
    }


def get_memory_index_settings(config: OpenSearchConfig) -> dict[str, Any]:
    """Get index settings for conversation memory.

    Args:
        config: OpenSearch configuration.

    Returns:
        Index settings dictionary.
    """
    return {
        "index": {
            "number_of_shards": 1,  # Memory is typically smaller
            "number_of_replicas": config.number_of_replicas,
            "refresh_interval": "1s",
        }
    }


def get_memory_index_mappings() -> dict[str, Any]:
    """Get index mappings for conversation memory.

    Returns:
        Index mappings dictionary.
    """
    return {
        "properties": {
            "conversation_id": {"type": "keyword"},
            "account_id": {"type": "keyword"},
            "user_id": {"type": "keyword"},
            "message_index": {"type": "integer"},
            "role": {"type": "keyword"},  # user, assistant, system
            "content": {"type": "text"},
            "metadata": {"type": "object", "enabled": True, "dynamic": True},
            "created_at": {"type": "date"},
            "expires_at": {"type": "date"},
        }
    }


def get_index_template(
    config: OpenSearchConfig,
    index_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """Get index template for knowledge indices.

    Args:
        config: OpenSearch configuration.
        index_patterns: Index patterns to match (default: ["{prefix}-*"]).

    Returns:
        Index template dictionary.
    """
    if index_patterns is None:
        index_patterns = [f"{config.index_prefix}-*"]

    return {
        "index_patterns": index_patterns,
        "template": {
            "settings": get_knowledge_index_settings(config),
            "mappings": get_knowledge_index_mappings(config),
        },
        "priority": 200,  # Higher than default gnosisllm-template (100)
        "version": 1,
    }


def get_ingest_pipeline(config: OpenSearchConfig) -> dict[str, Any]:
    """Get ingest pipeline for document processing.

    Creates a pipeline that:
    1. Generates embeddings using the deployed ML model
    2. Sets indexed_at timestamp
    3. Calculates word count

    Args:
        config: OpenSearch configuration.

    Returns:
        Ingest pipeline dictionary.
    """
    processors: list[dict[str, Any]] = []

    # Text embedding processor (requires model_id)
    if config.model_id:
        processors.append({
            "text_embedding": {
                "model_id": config.model_id,
                "field_map": {
                    "content": config.embedding_field,  # content -> content_embedding
                },
            }
        })

    # Set indexed_at timestamp
    processors.append({
        "set": {
            "field": "indexed_at",
            "value": "{{_ingest.timestamp}}",
        }
    })

    # Calculate word count
    processors.append({
        "script": {
            "description": "Calculate word count",
            "source": """
                if (ctx.content != null) {
                    ctx.word_count = ctx.content.split("\\\\s+").length;
                }
            """,
            "ignore_failure": True,
        }
    })

    return {
        "description": "GnosisLLM knowledge document ingest pipeline",
        "processors": processors,
    }


def get_search_pipeline(config: OpenSearchConfig) -> dict[str, Any]:
    """Get search pipeline for hybrid search score normalization.

    Uses min_max normalization and arithmetic_mean combination
    for hybrid neural + keyword search.

    Args:
        config: OpenSearch configuration.

    Returns:
        Search pipeline dictionary.
    """
    return {
        "description": "GnosisLLM search pipeline for hybrid search",
        "phase_results_processors": [
            {
                "normalization-processor": {
                    "normalization": {"technique": "min_max"},
                    "combination": {
                        "technique": "arithmetic_mean",
                        "parameters": {"weights": [0.7, 0.3]},  # semantic, keyword
                    },
                }
            }
        ],
    }
