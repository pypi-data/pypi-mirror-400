from __future__ import annotations

import math
import struct
from typing import Any, Iterator, Sequence
from urllib.parse import urlparse

import grpc

from casper_client.errors import CasperError, CasperErrorKind
from casper_client.http import ApiClient
from casper_client.models import (
    CollectionInfo,
    CollectionsListResponse,
    GetVectorResponse,
    MatrixInfo,
    PQInfo,
    SearchResult,
    UploadMatrixResult,
)


def _strip_scheme(host: str) -> str:
    if host.startswith("http://") or host.startswith("https://"):
        parsed = urlparse(host)
        if parsed.hostname:
            return parsed.hostname
        return host.split("://", 1)[1]
    return host


class CasperClient:
    """
    High-level Casper HTTP/gRPC client.
    """

    def __init__(
        self,
        *,
        host: str = "http://127.0.0.1",
        http_port: int = 8080,
        grpc_port: int = 50051,
        timeout: float | None = 30.0,
        **httpx_kwargs: Any,
    ) -> None:
        base = host.rstrip("/")
        if not (base.startswith("http://") or base.startswith("https://")):
            base = "http://" + base

        self._rest_uri = f"{base}:{http_port}"
        self._grpc_addr = f"{_strip_scheme(host)}:{grpc_port}"
        self._http = ApiClient(self._rest_uri, timeout=timeout, **httpx_kwargs)

    @property
    def rest_uri(self) -> str:
        return self._rest_uri

    @property
    def grpc_addr(self) -> str:
        return self._grpc_addr

    def close(self) -> None:
        self._http.close()

    # -------------------------
    # Health
    # -------------------------

    def health(self) -> None:
        self._http.request_bytes(method="GET", url="/health")

    # -------------------------
    # Collections
    # -------------------------

    def list_collections(self) -> CollectionsListResponse:
        data = self._http.request_json(method="GET", url="/collections")
        if not isinstance(data, dict):
            raise CasperError(
                kind=CasperErrorKind.INVALID_RESPONSE,
                message="expected JSON object from /collections",
            )
        return CollectionsListResponse.from_dict(data)

    def get_collection(self, name: str) -> CollectionInfo:
        data = self._http.request_json(method="GET", url="/collection/{name}", path_params={"name": name})
        if not isinstance(data, dict):
            raise CasperError(
                kind=CasperErrorKind.INVALID_RESPONSE,
                message="expected JSON object from /collection/{name}",
            )
        return CollectionInfo.from_dict(data)

    def create_collection(self, name: str, *, dim: int, max_size: int) -> None:
        self._http.request_bytes(
            method="POST",
            url="/collection/{name}",
            path_params={"name": name},
            params={"dim": dim, "max_size": max_size},
            headers={"Content-Type": "application/json"},
        )

    def delete_collection(self, name: str) -> None:
        self._http.request_bytes(method="DELETE", url="/collection/{name}", path_params={"name": name})

    def mute_collection(self, name: str) -> None:
        self._http.request_bytes(method="POST", url="/collection/{name}/mute", path_params={"name": name})

    def unmute_collection(self, name: str) -> None:
        self._http.request_bytes(method="POST", url="/collection/{name}/unmute", path_params={"name": name})

    # -------------------------
    # Vectors
    # -------------------------

    def insert_vector(self, collection: str, *, id: int, vector: Sequence[float]) -> None:
        self._http.request_bytes(
            method="POST",
            url="/collection/{name}/insert",
            path_params={"name": collection},
            params={"id": id},
            json={"vector": list(vector)},
            headers={"Content-Type": "application/json"},
        )

    def delete_vector(self, collection: str, *, id: int) -> None:
        self._http.request_bytes(
            method="DELETE",
            url="/collection/{name}/delete",
            path_params={"name": collection},
            params={"id": id},
            headers={"Content-Type": "application/json"},
        )

    def get_vector(self, collection: str, *, id: int) -> GetVectorResponse:
        data = self._http.request_json(
            method="GET", url="/collection/{name}/vector/{id}", path_params={"name": collection, "id": id}
        )
        if not isinstance(data, dict):
            raise CasperError(
                kind=CasperErrorKind.INVALID_RESPONSE,
                message="expected JSON object from /collection/{name}/vector/{id}",
            )
        return GetVectorResponse.from_dict(data)

    def batch_update(
        self,
        collection: str,
        *,
        insert: Sequence[dict[str, Any]] | None = None,
        delete: Sequence[int] | None = None,
    ) -> None:
        payload = {
            "insert": list(insert) if insert is not None else [],
            "delete": list(delete) if delete is not None else [],
        }
        self._http.request_bytes(
            method="POST",
            url="/collection/{name}/update",
            path_params={"name": collection},
            json=payload,
            headers={"Content-Type": "application/json"},
        )

    # -------------------------
    # Indexes
    # -------------------------

    def create_hnsw_index(
        self,
        collection: str,
        *,
        metric: str,
        quantization: str,
        m: int,
        m0: int,
        ef_construction: int,
        pq_name: str | None = None,
        normalization: bool | None = None,
    ) -> None:
        hnsw: dict[str, Any] = {
            "metric": metric,
            "quantization": quantization,
            "m": m,
            "m0": m0,
            "ef_construction": ef_construction,
        }
        if pq_name is not None:
            hnsw["pq_name"] = pq_name

        body: dict[str, Any] = {"hnsw": hnsw}
        if normalization is not None:
            body["normalization"] = normalization

        self._http.request_bytes(
            method="POST",
            url="/collection/{name}/index",
            path_params={"name": collection},
            json=body,
            headers={"Content-Type": "application/json"},
        )

    def delete_index(self, collection: str) -> None:
        self._http.request_bytes(method="DELETE", url="/collection/{name}/index", path_params={"name": collection})

    # -------------------------
    # Search
    # -------------------------

    def search(self, collection: str, *, query: Sequence[float], limit: int, output: str = "bin") -> list[SearchResult]:
        if output not in ("bin", "json"):
            raise CasperError(kind=CasperErrorKind.CLIENT, message="output must be 'bin' or 'json'")

        if output == "bin":
            raw = self._http.request_bytes(
                method="POST",
                url="/collection/{name}/search",
                path_params={"name": collection},
                params={"limit": limit, "output": "bin"},
                json={"vector": list(query)},
                headers={"Content-Type": "application/json"},
            )
            return self._decode_search_bin(raw)

        data = self._http.request_json(
            method="POST",
            url="/collection/{name}/search",
            path_params={"name": collection},
            params={"limit": limit, "output": "json"},
            json={"vector": list(query)},
            headers={"Content-Type": "application/json"},
        )
        if not isinstance(data, list):
            raise CasperError(kind=CasperErrorKind.INVALID_RESPONSE, message="expected JSON array from search")
        out: list[SearchResult] = []
        for item in data:
            if isinstance(item, list) and len(item) == 2:
                out.append(SearchResult(id=int(item[0]), score=float(item[1])))
        return out

    @staticmethod
    def _decode_search_bin(buf: bytes) -> list[SearchResult]:
        if len(buf) < 4:
            raise CasperError(kind=CasperErrorKind.INVALID_RESPONSE, message="binary search response too short")
        (count,) = struct.unpack_from("<I", buf, 0)
        expected = 4 + int(count) * 8
        if len(buf) < expected:
            raise CasperError(
                kind=CasperErrorKind.INVALID_RESPONSE,
                message=f"binary search response truncated: expected at least {expected} bytes, got {len(buf)}",
            )
        out: list[SearchResult] = []
        offset = 4
        for _ in range(int(count)):
            id_u32, score_f32 = struct.unpack_from("<If", buf, offset)
            out.append(SearchResult(id=int(id_u32), score=float(score_f32)))
            offset += 8
        return out

    # -------------------------
    # Matrix HTTP
    # -------------------------

    def list_matrices(self) -> list[MatrixInfo]:
        data = self._http.request_json(method="GET", url="/matrix/list", headers={"Content-Type": "application/json"})
        if not isinstance(data, list):
            raise CasperError(kind=CasperErrorKind.INVALID_RESPONSE, message="expected JSON array from /matrix/list")
        return [MatrixInfo.from_dict(x) for x in data if isinstance(x, dict)]

    def get_matrix_info(self, name: str) -> MatrixInfo:
        data = self._http.request_json(
            method="GET", url="/matrix/{name}", path_params={"name": name}, headers={"Content-Type": "application/json"}
        )
        if not isinstance(data, dict):
            raise CasperError(kind=CasperErrorKind.INVALID_RESPONSE, message="expected JSON object from /matrix/{name}")
        return MatrixInfo.from_dict(data)

    def delete_matrix(self, name: str) -> None:
        self._http.request_bytes(
            method="DELETE", url="/matrix/{name}", path_params={"name": name}, headers={"Content-Type": "application/json"}
        )

    # -------------------------
    # PQ
    # -------------------------

    def create_pq(self, name: str, *, dim: int, codebooks: Sequence[str]) -> None:
        self._http.request_bytes(
            method="POST",
            url="/pq/{name}",
            path_params={"name": name},
            json={"dim": dim, "codebooks": list(codebooks)},
            headers={"Content-Type": "application/json"},
        )

    def delete_pq(self, name: str) -> None:
        self._http.request_bytes(
            method="DELETE", url="/pq/{name}", path_params={"name": name}, headers={"Content-Type": "application/json"}
        )

    def list_pqs(self) -> list[PQInfo]:
        data = self._http.request_json(method="GET", url="/pq/list", headers={"Content-Type": "application/json"})
        if not isinstance(data, list):
            raise CasperError(kind=CasperErrorKind.INVALID_RESPONSE, message="expected JSON array from /pq/list")
        return [PQInfo.from_dict(x) for x in data if isinstance(x, dict)]

    def get_pq_info(self, name: str) -> PQInfo:
        data = self._http.request_json(
            method="GET", url="/pq/{name}", path_params={"name": name}, headers={"Content-Type": "application/json"}
        )
        if not isinstance(data, dict):
            raise CasperError(kind=CasperErrorKind.INVALID_RESPONSE, message="expected JSON object from /pq/{name}")
        return PQInfo.from_dict(data)

    # -------------------------
    # gRPC UploadMatrix
    # -------------------------

    def upload_matrix(
        self,
        *,
        name: str,
        dimension: int,
        vectors: Sequence[Sequence[float]] | Sequence[float],
        chunk_floats: int | None = None,
    ) -> UploadMatrixResult:
        if dimension <= 0:
            raise CasperError(kind=CasperErrorKind.CLIENT, message="dimension must be greater than 0")

        flat = self._flatten_vectors(vectors)
        if len(flat) % dimension != 0:
            raise CasperError(
                kind=CasperErrorKind.CLIENT,
                message=f"vector buffer length {len(flat)} is not divisible by dimension {dimension}",
            )

        if chunk_floats is None or chunk_floats < dimension:
            chunk_floats = dimension

        from casper_client.grpc import matrix_service_pb2 as pb2
        from casper_client.grpc import matrix_service_pb2_grpc as pb2_grpc

        total_floats = len(flat)
        total_chunks = int(math.ceil(total_floats / float(chunk_floats)))

        max_vectors_per_chunk = max(1, chunk_floats // dimension)
        header = pb2.MatrixHeader(
            name=name,
            dimension=int(dimension),
            total_chunks=int(total_chunks),
            max_vectors_per_chunk=int(max_vectors_per_chunk),
        )

        def gen() -> Iterator[pb2.UploadMatrixRequest]:
            yield pb2.UploadMatrixRequest(header=header)
            for chunk_idx in range(total_chunks):
                start = chunk_idx * chunk_floats
                end = min(start + chunk_floats, total_floats)
                yield pb2.UploadMatrixRequest(
                    data=pb2.MatrixData(chunk_index=chunk_idx + 1, vector=flat[start:end])
                )

        try:
            with grpc.insecure_channel(self._grpc_addr) as channel:
                stub = pb2_grpc.MatrixServiceStub(channel)
                resp = stub.UploadMatrix(gen())
        except Exception as e:
            raise CasperError(kind=CasperErrorKind.CLIENT, message="UploadMatrix failed", cause=e) from e

        return UploadMatrixResult(total_vectors=int(resp.total_vectors), total_chunks=int(resp.total_chunks))

    @staticmethod
    def _flatten_vectors(vectors: Sequence[Sequence[float]] | Sequence[float]) -> list[float]:
        if len(vectors) == 0:
            return []
        first = vectors[0]  # type: ignore[index]
        if isinstance(first, (int, float)):
            return [float(x) for x in vectors]  # type: ignore[arg-type]
        out: list[float] = []
        for row in vectors:  # type: ignore[assignment]
            out.extend(float(x) for x in row)
        return out


