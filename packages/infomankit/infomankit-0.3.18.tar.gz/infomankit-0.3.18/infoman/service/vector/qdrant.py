#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Iterable, Sequence

from .base import VectorClient, VectorPoint, VectorFilter

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter as QFilter,
        FieldCondition,
        MatchAny,
        MatchValue,
    )
except Exception:  # pragma: no cover - optional dependency at import time
    AsyncQdrantClient = None  # type: ignore
    Distance = VectorParams = PointStruct = object  # type: ignore
    QFilter = FieldCondition = MatchAny = MatchValue = object  # type: ignore


_DIST_MAP = {
    "cosine": Distance.COSINE if hasattr(Distance, "COSINE") else "cosine",
    "dot": Distance.DOT if hasattr(Distance, "DOT") else "dot",
    "euclid": Distance.EUCLID if hasattr(Distance, "EUCLID") else "euclid",
}


def _to_qfilter(f: VectorFilter | None) -> QFilter | None:
    if f is None:
        return None
    must = []
    must_not = []
    if f.must:
        for k, v in f.must.items():
            if isinstance(v, (list, tuple, set)):
                must.append(FieldCondition(key=k, match=MatchAny(any=list(v))))
            else:
                must.append(FieldCondition(key=k, match=MatchValue(value=v)))
    if f.must_not:
        for k, v in f.must_not.items():
            if isinstance(v, (list, tuple, set)):
                must_not.append(FieldCondition(key=k, match=MatchAny(any=list(v))))
            else:
                must_not.append(FieldCondition(key=k, match=MatchValue(value=v)))
    return QFilter(must=must or None, must_not=must_not or None)


class QdrantVectorClient(VectorClient):
    def __init__(self, client: Any):
        if AsyncQdrantClient is not None and not isinstance(client, AsyncQdrantClient):
            # Allow duck typing (useful in tests), but warn in docs
            pass
        self.client = client

    async def ensure_collection(
        self, name: str, vector_size: int, distance: str = "cosine", on_disk: bool = False
    ) -> None:
        dist = _DIST_MAP.get(distance, _DIST_MAP["cosine"])
        exists = await self.client.collection_exists(collection_name=name)
        if exists:
            return
        await self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=dist, on_disk=on_disk),
        )

    async def upsert(self, collection: str, points: Iterable[VectorPoint], wait: bool = False) -> None:
        payloads = []
        qpoints: list[PointStruct] = []
        for p in points:
            payload = dict(p.payload) if p.payload else None
            payloads.append(payload)
            qpoints.append(PointStruct(id=p.id, vector=list(p.vector), payload=payload))
        if not qpoints:
            return
        await self.client.upsert(collection_name=collection, points=qpoints, wait=wait)

    async def delete(
        self,
        collection: str,
        ids: Iterable[str | int] | None = None,
        filt: VectorFilter | None = None,
        wait: bool = False,
    ) -> None:
        if ids:
            await self.client.delete(collection_name=collection, points=list(ids), wait=wait)
            return
        qf = _to_qfilter(filt)
        if qf is not None:
            await self.client.delete(collection_name=collection, filter=qf, wait=wait)

    async def search(
        self,
        collection: str,
        query_vector: Sequence[float],
        limit: int = 10,
        filt: VectorFilter | None = None,
        with_vectors: bool = False,
    ) -> list[dict[str, Any]]:
        qf = _to_qfilter(filt)
        res = await self.client.search(
            collection_name=collection,
            query_vector=list(query_vector),
            limit=limit,
            filter=qf,
            with_vectors=with_vectors,
        )
        results: list[dict[str, Any]] = []
        for r in res:
            results.append(
                {
                    "id": r.id,
                    "score": r.score,
                    "payload": getattr(r, "payload", None),
                    "vector": getattr(r, "vector", None) if with_vectors else None,
                }
            )
        return results

