"""
Memvid v2 - High-performance AI memory library

This module provides Python bindings for memvid-core v2, enabling:
- Single-file .mv2 memory storage
- Full-text search with BM25 ranking
- PDF document ingestion
- Crash-safe append-only writes
"""

from memvid_rs._memvid_rs import MemvidMemory

__version__ = "2.0.1"
__all__ = ["MemvidMemory"]
