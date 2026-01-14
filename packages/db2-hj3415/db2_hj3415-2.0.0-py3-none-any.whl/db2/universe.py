# src/db2/universe.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Literal, TypedDict

from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.database import AsyncDatabase


UniverseName = str  # ex) "krx300", "kospi200", "us_nasdaq100" ...
UNIVERSE_LATEST_COL = "universe_latest"
UNIVERSE_SNAPSHOTS_COL = "universe_snapshots"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UniverseItem(TypedDict, total=False):
    """
    최소 확장 대비:
    - code: 식별자(필수)
    - name: 표시명(옵션)
    - market: KRX/US 등 (옵션)
    - meta: 기타(옵션)
    """
    code: str
    name: str
    market: str
    meta: dict[str, Any]


class UniverseLatestDoc(TypedDict):
    _id: str                 # universe_name
    universe: str
    asof: datetime
    source: str              # ex) "samsungfund"
    items: list[UniverseItem]


class UniverseSnapshotDoc(TypedDict):
    universe: str
    asof: datetime
    source: str
    items: list[UniverseItem]


def _normalize_items(items: Iterable[Any]) -> list[UniverseItem]:
    """
    krx 프로젝트 CodeItem(dataclass) / dict / pydantic model 등
    최대한 받아서 UniverseItem(list[dict])로 정규화.
    """
    out: list[UniverseItem] = []
    for it in items:
        if it is None:
            continue

        # pydantic v2
        if hasattr(it, "model_dump"):
            d = it.model_dump()
        elif isinstance(it, dict):
            d = dict(it)
        else:
            # dataclass / 객체 접근 fallback
            d = {
                "code": getattr(it, "code", None),
                "name": getattr(it, "name", None),
                "market": getattr(it, "market", None),
                "meta": getattr(it, "meta", None),
            }

        code = (d.get("code") or "").strip()
        if not code:
            continue

        item: UniverseItem = {"code": code}
        name = d.get("name")
        if isinstance(name, str) and name.strip():
            item["name"] = name.strip()

        market = d.get("market")
        if isinstance(market, str) and market.strip():
            item["market"] = market.strip()

        meta = d.get("meta")
        if isinstance(meta, dict) and meta:
            item["meta"] = meta

        out.append(item)

    return out


async def ensure_indexes_universe(db: AsyncDatabase) -> None:
    latest = db[UNIVERSE_LATEST_COL]
    snaps = db[UNIVERSE_SNAPSHOTS_COL]

    # latest는 _id=universe (기본 유니크) + asof 조회용
    await latest.create_index([("universe", ASCENDING)])  # 선택(명시)
    await latest.create_index([("asof", DESCENDING)])

    # snapshots는 universe 타임라인 조회
    await snaps.create_index([("universe", ASCENDING), ("asof", DESCENDING)])

    # items.code로 검색할 일은 보통 krx 쪽에서 메모리로 처리하니 필수는 아님
    # 필요해지면 multikey index 추가 가능:
    # await snaps.create_index([("universe", ASCENDING), ("items.code", ASCENDING)])


async def upsert_universe_latest(
    db: AsyncDatabase,
    *,
    universe: UniverseName,
    items: Iterable[Any],
    asof: datetime | None = None,
    source: str = "unknown",
) -> None:
    doc: UniverseLatestDoc = {
        "_id": universe,
        "universe": universe,
        "asof": asof or _utcnow(),
        "source": source,
        "items": _normalize_items(items),
    }
    await db[UNIVERSE_LATEST_COL].update_one(
        {"_id": universe},
        {"$set": doc},
        upsert=True,
    )


async def insert_universe_snapshot(
    db: AsyncDatabase,
    *,
    universe: UniverseName,
    items: Iterable[Any],
    asof: datetime | None = None,
    source: str = "unknown",
) -> None:
    doc: UniverseSnapshotDoc = {
        "universe": universe,
        "asof": asof or _utcnow(),
        "source": source,
        "items": _normalize_items(items),
    }
    await db[UNIVERSE_SNAPSHOTS_COL].insert_one(doc)


async def get_universe_latest(
    db: AsyncDatabase,
    *,
    universe: UniverseName,
) -> UniverseLatestDoc | None:
    doc = await db[UNIVERSE_LATEST_COL].find_one({"_id": universe})
    return doc


async def list_universe_snapshots(
    db: AsyncDatabase,
    *,
    universe: UniverseName,
    limit: int = 30,
    desc: bool = True,
) -> list[dict[str, Any]]:
    order = DESCENDING if desc else ASCENDING
    cur = (
        db[UNIVERSE_SNAPSHOTS_COL]
        .find({"universe": universe})
        .sort("asof", order)
        .limit(limit)
    )
    return await cur.to_list(length=limit)