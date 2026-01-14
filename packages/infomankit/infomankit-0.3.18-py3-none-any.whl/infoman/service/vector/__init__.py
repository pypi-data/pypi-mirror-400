#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Vector store integration entry.

Exposes a light-weight abstraction and a Qdrant implementation.
"""

from .base import VectorClient, VectorPoint, VectorFilter
from .qdrant import QdrantVectorClient
from .service import VectorService, get_vector_service

__all__ = [
    "VectorClient",
    "VectorPoint",
    "VectorFilter",
    "QdrantVectorClient",
    "VectorService",
    "get_vector_service",
]
