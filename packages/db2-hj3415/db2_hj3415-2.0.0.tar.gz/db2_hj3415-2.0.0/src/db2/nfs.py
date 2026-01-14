# src/db2/nfs.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Literal, TypedDict, Sequence

from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.database import AsyncDatabase
from pymongo import UpdateOne

from .hash_utils import stable_sha256


Endpoint = Literal["c101", "c103", "c104", "c106", "c108"]


class LatestDoc(TypedDict):
    _id: str
    endpoint: str
    code: str
    asof: datetime
    payload: dict[str, Any]
    payload_hash: str


class SnapshotDoc(TypedDict):
    endpoint: str
    code: str
    asof: datetime
    payload: dict[str, Any]
    payload_hash: str


LATEST_COL = "latest"
SNAPSHOTS_COL = "snapshots"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _latest_id(endpoint: Endpoint, code: str) -> str:
    return f"{endpoint}:{code}"


def _dto_to_payload(dto: Any) -> dict[str, Any]:
    """
    scraper2/contracts 쪽 DTO는 pydantic v2라 model_dump()가 있음.
    dict/기타도 최대한 받아줌.
    """
    if dto is None:
        return {}
    if hasattr(dto, "model_dump"):
        return dto.model_dump()
    if isinstance(dto, dict):
        return dto
    # 최후 fallback
    return {"value": str(dto)}


async def ensure_indexes(
    db: AsyncDatabase,
    *,
    snapshot_ttl_days: int | None,
) -> None:
    latest = db[LATEST_COL]
    snapshots = db[SNAPSHOTS_COL]

    # latest: endpoint+code 보조 인덱스
    await latest.create_index([("endpoint", ASCENDING), ("code", ASCENDING)])

    # snapshots: 코드별 타임라인 조회
    await snapshots.create_index(
        [("endpoint", ASCENDING), ("code", ASCENDING), ("asof", DESCENDING)]
    )

    # endpoint없이 코드만으로 삭제를 많이할경우 성능향상
    await latest.create_index([("code", ASCENDING)])
    await snapshots.create_index([("code", ASCENDING)])

    # ✅ TTL: asof 기준으로 오래된 스냅샷 자동 삭제
    # - expireAfterSeconds 는 "초" 단위
    # - TTL 인덱스는 단일 필드 인덱스여야 함
    if snapshot_ttl_days is not None:
        expire_seconds = int(snapshot_ttl_days) * 24 * 60 * 60
        await snapshots.create_index(
            [("asof", ASCENDING)],
            expireAfterSeconds=expire_seconds,
            name="ttl_asof",
        )


async def upsert_latest(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    dto: Any,
    asof: datetime | None = None,
) -> None:
    payload = _dto_to_payload(dto)
    code = payload.get("코드") or getattr(dto, "코드", None)
    if not code:
        raise ValueError("DTO payload must include '코드'")

    doc: LatestDoc = {
        "_id": _latest_id(endpoint, str(code)),
        "endpoint": endpoint,
        "code": str(code),
        "asof": asof or _utcnow(),
        "payload": payload,
        "payload_hash": stable_sha256(payload),
    }

    await db[LATEST_COL].update_one(
        {"_id": doc["_id"]},
        {"$set": doc},
        upsert=True,
    )


async def upsert_latest_many(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    dtos: Iterable[Any],
    asof: datetime | None = None,
) -> None:
    """
    간단/명확 우선: 한 건씩 upsert.
    (300종목이면 충분히 빠름. 나중에 bulk_write로 바꿔도 됨)
    """
    for dto in dtos:
        await upsert_latest(db, endpoint=endpoint, dto=dto, asof=asof)


async def insert_snapshot(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    dto: Any,
    asof: datetime | None = None,
) -> None:
    payload = _dto_to_payload(dto)
    code = payload.get("코드") or getattr(dto, "코드", None)
    if not code:
        raise ValueError("DTO payload must include '코드'")

    doc: SnapshotDoc = {
        "endpoint": endpoint,
        "code": str(code),
        "asof": asof or _utcnow(),
        "payload": payload,
        "payload_hash": stable_sha256(payload),
    }
    await db[SNAPSHOTS_COL].insert_one(doc)


async def insert_snapshots_many(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    dtos: Iterable[Any],
    asof: datetime | None = None,
) -> None:
    docs: list[SnapshotDoc] = []
    ts = asof or _utcnow()
    for dto in dtos:
        payload = _dto_to_payload(dto)
        code = payload.get("코드") or getattr(dto, "코드", None)
        if not code:
            continue
        docs.append(
            {
                "endpoint": endpoint,
                "code": str(code),
                "asof": ts,
                "payload": payload,
                "payload_hash": stable_sha256(payload),
            }
        )

    if docs:
        await db[SNAPSHOTS_COL].insert_many(docs)


async def get_latest(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    code: str,
) -> dict[str, Any] | None:
    doc = await db[LATEST_COL].find_one({"_id": _latest_id(endpoint, code)})
    if not doc:
        return None
    return doc


async def list_snapshots(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    code: str,
    limit: int = 50,
    desc: bool = True,
) -> list[dict[str, Any]]:
    order = DESCENDING if desc else ASCENDING
    cur = db[SNAPSHOTS_COL].find({"endpoint": endpoint, "code": code}).sort("asof", order).limit(limit)
    return await cur.to_list(length=limit)


async def delete_code_from_nfs(
    db: AsyncDatabase,
    *,
    code: str,
    endpoint: Endpoint | None = None,
) -> dict[str, int]:
    """
    nfs DB에서 특정 code 관련 데이터를 삭제한다.
    - endpoint=None: c101..c108 전체에서 삭제
    - endpoint 지정: 해당 endpoint만 삭제
    반환: {"latest_deleted": x, "snapshots_deleted": y}
    """
    code = str(code).strip()
    if not code:
        return {"latest_deleted": 0, "snapshots_deleted": 0}

    latest_filter: dict[str, Any] = {"code": code}
    snaps_filter: dict[str, Any] = {"code": code}
    if endpoint is not None:
        latest_filter["endpoint"] = endpoint
        snaps_filter["endpoint"] = endpoint

    r1 = await db[LATEST_COL].delete_many(latest_filter)
    r2 = await db[SNAPSHOTS_COL].delete_many(snaps_filter)

    return {"latest_deleted": int(r1.deleted_count), "snapshots_deleted": int(r2.deleted_count)}


async def delete_codes_from_nfs(
    db: AsyncDatabase,
    *,
    codes: Sequence[str],
    endpoint: Endpoint | None = None,
) -> dict[str, int]:
    """
    여러 code를 한 번에 삭제.
    """
    codes_ = [str(c).strip() for c in codes if c and str(c).strip()]
    if not codes_:
        return {"latest_deleted": 0, "snapshots_deleted": 0}

    latest_filter: dict[str, Any] = {"code": {"$in": codes_}}
    snaps_filter: dict[str, Any] = {"code": {"$in": codes_}}
    if endpoint is not None:
        latest_filter["endpoint"] = endpoint
        snaps_filter["endpoint"] = endpoint

    r1 = await db[LATEST_COL].delete_many(latest_filter)
    r2 = await db[SNAPSHOTS_COL].delete_many(snaps_filter)

    return {"latest_deleted": int(r1.deleted_count), "snapshots_deleted": int(r2.deleted_count)}


# ---- delete helpers (intention-revealing wrappers) ----

ALL_ENDPOINTS: tuple[Endpoint, ...] = ("c101", "c103", "c104", "c106", "c108")


def _clean_codes(codes: Sequence[str]) -> list[str]:
    # strip + remove empty + dedupe preserve order
    out: list[str] = []
    for c in codes:
        s = str(c).strip()
        if s:
            out.append(s)

    seen: set[str] = set()
    uniq: list[str] = []
    for c in out:
        if c in seen:
            continue
        seen.add(c)
        uniq.append(c)
    return uniq


async def delete_latest_codes(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    codes: Sequence[str],
) -> int:
    """
    특정 endpoint의 latest에서만 codes 삭제.
    반환: deleted_count
    """
    codes_ = _clean_codes(codes)
    if not codes_:
        return 0

    r = await db[LATEST_COL].delete_many({"endpoint": endpoint, "code": {"$in": codes_}})
    return int(r.deleted_count)


async def delete_snapshot_codes(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    codes: Sequence[str],
) -> int:
    """
    특정 endpoint의 snapshots에서만 codes 삭제.
    반환: deleted_count
    """
    codes_ = _clean_codes(codes)
    if not codes_:
        return 0

    r = await db[SNAPSHOTS_COL].delete_many({"endpoint": endpoint, "code": {"$in": codes_}})
    return int(r.deleted_count)


async def delete_codes_for_endpoint(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    codes: Sequence[str],
) -> dict[str, int]:
    """
    특정 endpoint에 대해서 latest+snapshots 함께 삭제.
    (delete_codes_from_nfs(endpoint=...)와 동일 동작이지만 이름이 더 명확함)
    """
    # 기존 구현 재사용
    return await delete_codes_from_nfs(db, codes=codes, endpoint=endpoint)


async def delete_codes_from_all_endpoints(
    db: AsyncDatabase,
    *,
    codes: Sequence[str],
) -> dict[str, int]:
    """
    모든 endpoint(c101,c103,c104,c106,c108)를 대상으로 latest+snapshots 삭제.
    (delete_codes_from_nfs(endpoint=None)와 동일 동작이지만 의도를 함수명으로 고정)
    """
    # 기존 구현 재사용
    return await delete_codes_from_nfs(db, codes=codes, endpoint=None)


async def delete_code_everywhere(
    db: AsyncDatabase,
    *,
    code: str,
) -> dict[str, int]:
    """
    단일 code를 모든 endpoint에서 삭제.
    (delete_code_from_nfs(endpoint=None) 의도 명확 버전)
    """
    return await delete_code_from_nfs(db, code=code, endpoint=None)


async def delete_code_for_endpoint(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    code: str,
) -> dict[str, int]:
    """
    단일 code를 특정 endpoint에서만 삭제.
    """
    return await delete_code_from_nfs(db, code=code, endpoint=endpoint)


async def delete_codes_split(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    codes: Sequence[str],
    latest: bool = True,
    snapshots: bool = True,
) -> dict[str, int]:
    """
    운영할 때 은근 유용한 옵션형:
    - latest만 / snapshots만 / 둘 다를 한 번에 제어

    반환: {"latest_deleted": x, "snapshots_deleted": y}
    """
    codes_ = _clean_codes(codes)
    if not codes_:
        return {"latest_deleted": 0, "snapshots_deleted": 0}

    latest_deleted = 0
    snapshots_deleted = 0

    if latest:
        r1 = await db[LATEST_COL].delete_many({"endpoint": endpoint, "code": {"$in": codes_}})
        latest_deleted = int(r1.deleted_count)

    if snapshots:
        r2 = await db[SNAPSHOTS_COL].delete_many({"endpoint": endpoint, "code": {"$in": codes_}})
        snapshots_deleted = int(r2.deleted_count)

    return {"latest_deleted": latest_deleted, "snapshots_deleted": snapshots_deleted}


# -----------------------------------------------------------------------------
# Hash diff helpers (change detection)
# -----------------------------------------------------------------------------


async def _get_latest_hash_map(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    codes: list[str] | None = None,
) -> dict[str, str]:
    """Return {code: payload_hash} from latest collection."""
    col = db[LATEST_COL]
    q: dict[str, Any] = {"endpoint": endpoint}
    if codes:
        q["code"] = {"$in": [str(c) for c in codes]}
    cur = col.find(q, {"code": 1, "payload_hash": 1})
    out: dict[str, str] = {}
    async for doc in cur:
        code = str(doc.get("code") or "")
        h = doc.get("payload_hash")
        if code and isinstance(h, str):
            out[code] = h
    return out


async def _get_prev_snapshot_hash_map(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    codes: list[str],
    before_asof: datetime | None = None,
) -> dict[str, str]:
    """Return {code: payload_hash} for the most recent snapshot per code."""
    if not codes:
        return {}

    col = db[SNAPSHOTS_COL]
    match: dict[str, Any] = {
        "endpoint": endpoint,
        "code": {"$in": [str(c) for c in codes]},
    }
    if before_asof is not None:
        match["asof"] = {"$lt": before_asof}

    pipeline = [
        {"$match": match},
        {"$sort": {"code": 1, "asof": -1}},
        {"$group": {"_id": "$code", "payload_hash": {"$first": "$payload_hash"}}},
    ]

    out: dict[str, str] = {}
    async for row in col.aggregate(pipeline):
        code = str(row.get("_id") or "")
        h = row.get("payload_hash")
        if code and isinstance(h, str):
            out[code] = h
    return out


async def diff_latest_vs_previous_snapshot(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    codes: list[str] | None = None,
    before_asof: datetime | None = None,
) -> dict[str, Any]:
    """Compare latest vs previous snapshot by payload hash.

    Returns
    - changed: hashes differ
    - new: latest exists but previous snapshot missing
    - missing_latest: snapshot exists but latest missing (rare)
    """
    latest_map = await _get_latest_hash_map(db, endpoint=endpoint, codes=codes)
    target_codes = list(latest_map.keys()) if codes is None else [str(c) for c in codes]

    prev_map = await _get_prev_snapshot_hash_map(
        db,
        endpoint=endpoint,
        codes=target_codes,
        before_asof=before_asof,
    )

    changed: list[str] = []
    new: list[str] = []
    for c in target_codes:
        lh = latest_map.get(c)
        ph = prev_map.get(c)
        if lh is None:
            continue
        if ph is None:
            new.append(c)
        elif lh != ph:
            changed.append(c)

    missing_latest = [c for c in prev_map.keys() if c not in latest_map]

    return {
        "endpoint": endpoint,
        "total_latest": len(latest_map),
        "total_prev": len(prev_map),
        "changed": changed,
        "new": new,
        "missing_latest": missing_latest,
    }
# -------------------------
# hash-based diff helpers
# -------------------------

async def list_snapshot_asofs(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    limit: int = 10,
) -> list[datetime]:
    """Return distinct snapshot batch times (asof) for an endpoint, newest first."""
    # We store snapshots in a single collection (SNAPSHOTS_COL) with endpoint field.
    cur = (
        db[SNAPSHOTS_COL]
        .find({"endpoint": endpoint}, {"asof": 1})
        .sort("asof", DESCENDING)
        .limit(max(limit * 5, 50))
    )

    seen: set[datetime] = set()
    out: list[datetime] = []
    async for doc in cur:
        asof = doc.get("asof")
        if not isinstance(asof, datetime):
            continue
        if asof in seen:
            continue
        seen.add(asof)
        out.append(asof)
        if len(out) >= limit:
            break
    return out


async def diff_two_snapshot_batches(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    newer_asof: datetime,
    older_asof: datetime,
    include_unchanged: bool = False,
) -> dict[str, Any]:
    """Compare two snapshot batches by payload_hash.

    Returns:
      {
        "endpoint": ..., "newer_asof": ..., "older_asof": ...,
        "changed_codes": [...],
        "new_codes": [...],
        "removed_codes": [...],
        "unchanged_codes": [...]  # optional
      }

    Notes:
    - "new" means code present in newer batch but not in older.
    - "removed" means code present in older batch but not in newer.
    - "changed" means both present and hash differs.
    """
    col = db[SNAPSHOTS_COL]

    pipeline: list[dict[str, Any]] = [
        {
            "$match": {
                "endpoint": endpoint,
                "asof": {"$in": [older_asof, newer_asof]},
            }
        },
        {
            "$project": {
                "code": 1,
                "asof": 1,
                "payload_hash": 1,
            }
        },
        {
            "$group": {
                "_id": "$code",
                "pairs": {
                    "$push": {
                        "asof": "$asof",
                        "h": "$payload_hash",
                    }
                },
            }
        },
        {
            "$project": {
                "code": "$_id",
                "older": {
                    "$first": {
                        "$filter": {
                            "input": "$pairs",
                            "as": "p",
                            "cond": {"$eq": ["$$p.asof", older_asof]},
                        }
                    }
                },
                "newer": {
                    "$first": {
                        "$filter": {
                            "input": "$pairs",
                            "as": "p",
                            "cond": {"$eq": ["$$p.asof", newer_asof]},
                        }
                    }
                },
            }
        },
    ]

    changed: list[str] = []
    unchanged: list[str] = []
    new_codes: list[str] = []
    removed_codes: list[str] = []

    async for row in col.aggregate(pipeline):
        code = row.get("code")
        if not code:
            continue

        older = row.get("older")
        newer = row.get("newer")

        older_h = older.get("h") if isinstance(older, dict) else None
        newer_h = newer.get("h") if isinstance(newer, dict) else None

        if older_h is None and newer_h is not None:
            new_codes.append(code)
            continue
        if older_h is not None and newer_h is None:
            removed_codes.append(code)
            continue
        if older_h is None and newer_h is None:
            continue

        if older_h != newer_h:
            changed.append(code)
        elif include_unchanged:
            unchanged.append(code)

    result: dict[str, Any] = {
        "endpoint": endpoint,
        "older_asof": older_asof,
        "newer_asof": newer_asof,
        "changed_codes": changed,
        "new_codes": new_codes,
        "removed_codes": removed_codes,
    }
    if include_unchanged:
        result["unchanged_codes"] = unchanged
    return result


async def diff_latest_snapshot_batches(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    include_unchanged: bool = False,
) -> dict[str, Any]:
    """Convenience: diff the newest snapshot batch vs the previous batch."""
    asofs = await list_snapshot_asofs(db, endpoint=endpoint, limit=2)
    if len(asofs) < 2:
        return {
            "endpoint": endpoint,
            "older_asof": None,
            "newer_asof": asofs[0] if asofs else None,
            "changed_codes": [],
            "new_codes": [],
            "removed_codes": [],
            "note": "need at least 2 snapshot batches",
        }

    newer_asof, older_asof = asofs[0], asofs[1]
    return await diff_two_snapshot_batches(
        db,
        endpoint=endpoint,
        newer_asof=newer_asof,
        older_asof=older_asof,
        include_unchanged=include_unchanged,
    )


async def backfill_payload_hashes(
    db: AsyncDatabase,
    *,
    endpoint: Endpoint,
    which: str = "snapshots",  # "latest"|"snapshots"|"both"
    batch_size: int = 500,
) -> dict[str, int]:
    """Backfill `payload_hash` for documents missing it.

    Safe to run multiple times; updates only docs missing `payload_hash`.
    """
    updated = 0

    async def _backfill_one(colname: str) -> int:
        nonlocal updated
        col = db[colname]

        cursor = col.find(
            {"endpoint": endpoint, "payload_hash": {"$exists": False}},
            {"_id": 1, "payload": 1},
            batch_size=batch_size,
        )

        ops: list[UpdateOne] = []
        async for row in cursor:
            _id = row.get("_id")
            payload = row.get("payload") or {}
            ops.append(
                UpdateOne(
                    {"_id": _id},
                    {"$set": {"payload_hash": stable_sha256(payload)}},
                )
            )

            if len(ops) >= batch_size:
                res = await col.bulk_write(ops, ordered=False)
                updated += int(res.modified_count)
                ops.clear()

        if ops:
            res = await col.bulk_write(ops, ordered=False)
            updated += int(res.modified_count)
            ops.clear()

        return updated

    if which in ("latest", "both"):
        await _backfill_one(LATEST_COL)
    if which in ("snapshots", "both"):
        await _backfill_one(SNAPSHOTS_COL)

    return {"updated": updated}