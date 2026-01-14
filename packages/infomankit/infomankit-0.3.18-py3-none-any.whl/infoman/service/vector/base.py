#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol, Sequence


@dataclass
class VectorPoint:
    id: str | int
    vector: Sequence[float]
    payload: Mapping[str, Any] | None = None


@dataclass
class VectorFilter:
    # Generic equality filter; concrete impl can translate
    must: dict[str, Any] | None = None
    must_not: dict[str, Any] | None = None


class VectorClient(Protocol):
    async def ensure_collection(
        self,
        name: str,
        vector_size: int,
        distance: str = "cosine",
        on_disk: bool = False,
    ) -> None: ...

    async def upsert(
        self,
        collection: str,
        points: Iterable[VectorPoint],
        wait: bool = False,
    ) -> None: ...

    async def delete(
        self,
        collection: str,
        ids: Iterable[str | int] | None = None,
        filt: VectorFilter | None = None,
        wait: bool = False,
    ) -> None: ...

    async def search(
        self,
        collection: str,
        query_vector: Sequence[float],
        limit: int = 10,
        filt: VectorFilter | None = None,
        with_vectors: bool = False,
    ) -> list[dict[str, Any]]: ...

