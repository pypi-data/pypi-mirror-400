#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Sequence

from fastapi import FastAPI

from .base import VectorPoint, VectorFilter
from . import VectorClient
from infoman.service.models.type.embed import (
    EmbedModel,
    EmbedCollection,
    EmbedDataType,
)


class VectorService:
    """High-level vector operations bound to Embed* config.

    This provides convenience methods using `EmbedModel` and `EmbedDataType`
    to compute collection names and dimensions.
    """

    def __init__(self, vector_client: VectorClient):
        self.vc = vector_client

    @staticmethod
    def collection_name(data_type: EmbedDataType, model: EmbedModel) -> str:
        return EmbedCollection.collection_name(data_type, model)

    async def ensure_collection(self, data_type: EmbedDataType, model: EmbedModel) -> str:
        name = self.collection_name(data_type, model)
        await self.vc.ensure_collection(name, model.value.dem, distance="cosine")
        return name

    async def upsert(
        self,
        data_type: EmbedDataType,
        model: EmbedModel,
        points: list[VectorPoint],
        wait: bool = False,
    ) -> str:
        name = self.collection_name(data_type, model)
        await self.vc.upsert(name, points, wait=wait)
        return name

    async def search(
        self,
        data_type: EmbedDataType,
        model: EmbedModel,
        query_vector: Sequence[float],
        limit: int = 10,
        filt: VectorFilter | None = None,
        with_vectors: bool = False,
    ) -> list[dict[str, Any]]:
        name = self.collection_name(data_type, model)
        return await self.vc.search(name, query_vector, limit, filt, with_vectors)


def get_vector_service(app: FastAPI) -> VectorService | None:
    vc = getattr(app.state, "vector_client", None)
    if vc is None:
        return None
    return VectorService(vc)

