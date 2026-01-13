"""Inference modules for batch and streaming BCI classification."""

from .batch import predict_batch, BatchResult
from .streaming import (
    StreamingSession,
    StreamingSessionSTS,
    ChunkResult,
    StreamingResult,
)
from .aggregation import (
    aggregate_chunks,
    compute_temporal_weights,
)

__all__ = [
    # Batch inference
    "predict_batch",
    "BatchResult",
    # Streaming inference
    "StreamingSession",
    "StreamingSessionSTS",
    "ChunkResult",
    "StreamingResult",
    # Aggregation
    "aggregate_chunks",
    "compute_temporal_weights",
]





