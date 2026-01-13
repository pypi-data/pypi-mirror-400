from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IndexInfo:
    index_type: str
    metric: str
    quantization: str
    normalization: bool
    max_elements: int | None = None
    m: int | None = None
    m0: int | None = None
    ef_construction: int | None = None
    ef: int | None = None

    @staticmethod
    def from_dict(data: dict) -> "IndexInfo":
        return IndexInfo(
            index_type=data.get("type", ""),
            metric=data.get("metric", ""),
            quantization=data.get("quantization", ""),
            normalization=bool(data.get("normalization", False)),
            max_elements=data.get("max_elements"),
            m=data.get("m"),
            m0=data.get("m0"),
            ef_construction=data.get("ef_construction"),
            ef=data.get("ef"),
        )


@dataclass
class CollectionInfo:
    name: str
    dimension: int
    mutable: bool
    has_index: bool
    max_size: int
    index: IndexInfo | None = None

    @staticmethod
    def from_dict(data: dict) -> "CollectionInfo":
        idx = data.get("index")
        return CollectionInfo(
            name=data.get("name", ""),
            dimension=int(data.get("dimension", 0)),
            mutable=bool(data.get("mutable", False)),
            has_index=bool(data.get("has_index", False)),
            max_size=int(data.get("max_size", 0)),
            index=IndexInfo.from_dict(idx) if isinstance(idx, dict) else None,
        )


@dataclass
class CollectionsListResponse:
    collections: list[CollectionInfo]

    @staticmethod
    def from_dict(data: dict) -> "CollectionsListResponse":
        cols = data.get("collections", [])
        if not isinstance(cols, list):
            cols = []
        return CollectionsListResponse(
            collections=[CollectionInfo.from_dict(c) for c in cols if isinstance(c, dict)]
        )


@dataclass
class SearchResult:
    id: int
    score: float


@dataclass
class GetVectorResponse:
    id: int
    vector: list[float]

    @staticmethod
    def from_dict(data: dict) -> "GetVectorResponse":
        return GetVectorResponse(
            id=int(data.get("id", 0)),
            vector=list(data.get("vector", [])) if isinstance(data.get("vector"), list) else [],
        )


@dataclass
class MatrixInfo:
    name: str
    dim: int
    length: int
    enabled: bool

    @staticmethod
    def from_dict(data: dict) -> "MatrixInfo":
        return MatrixInfo(
            name=data.get("name", ""),
            dim=int(data.get("dim", 0)),
            length=int(data.get("len", 0)),
            enabled=bool(data.get("enabled", False)),
        )


@dataclass
class PQInfo:
    name: str
    dim: int
    codebooks: list[str]
    enabled: bool

    @staticmethod
    def from_dict(data: dict) -> "PQInfo":
        codebooks = data.get("codebooks", [])
        return PQInfo(
            name=data.get("name", ""),
            dim=int(data.get("dim", 0)),
            codebooks=list(codebooks) if isinstance(codebooks, list) else [],
            enabled=bool(data.get("enabled", False)),
        )


@dataclass
class UploadMatrixResult:
    total_vectors: int
    total_chunks: int


