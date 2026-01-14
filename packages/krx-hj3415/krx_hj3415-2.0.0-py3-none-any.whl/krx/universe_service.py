# krx/universe_service.py
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable

from pymongo.asynchronous.database import AsyncDatabase

from .models import CodeItem, UniverseDiff, diff_universe
from .samsungfund import fetch_krx300_items


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _items_to_payload(items: list[CodeItem]) -> list[dict[str, Any]]:
    # db2에 저장할 때는 dict로 바꿔서 넣는 게 가장 단순함
    return [asdict(it) for it in items]


def _payload_to_items(payload: Any) -> list[CodeItem]:
    """
    db2 universe_latest 에 저장된 형태를 복원.
    payload가 아래 중 뭐든 대응:
      - {"items": [...]} 형태
      - {"payload": {"items": [...]}} 형태
      - 그냥 [...items...] 리스트
    """
    if payload is None:
        return []

    data = payload
    if isinstance(data, dict) and "payload" in data and isinstance(data["payload"], dict):
        data = data["payload"]

    if isinstance(data, dict) and "items" in data:
        data = data["items"]

    if not isinstance(data, list):
        return []

    out: list[CodeItem] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        code = str(row.get("code") or "").strip()
        if not code:
            continue
        name = str(row.get("name") or "").strip()
        market = row.get("market")
        asof_raw = row.get("asof")
        # asof는 DB에서 datetime으로 나오기도, ISO string으로 나오기도 함
        if isinstance(asof_raw, datetime):
            asof = asof_raw
        else:
            # fallback: 현재 시각 (정확도가 중요하면 ISO parse 추가)
            asof = _utcnow()
        out.append(CodeItem(code=code, name=name, asof=asof, market=market))
    return out


async def refresh_krx300(*, max_days: int = 15) -> tuple[datetime, list[CodeItem]]:
    # 현재는 KRX300만 구현. 다른 universe도 늘리면 여기서 분기
    return fetch_krx300_items(max_days=max_days)


async def refresh_and_diff(
    db: AsyncDatabase,
    *,
    universe: str = "krx300",
    max_days: int = 15,
    snapshot: bool = True,
) -> UniverseDiff:
    """
    1) 외부에서 최신 유니버스 수집
    2) DB에서 이전 latest 조회
    3) diff 계산
    4) latest upsert + (선택) snapshots insert
    """
    # --- 1) fetch ---
    if universe != "krx300":
        raise ValueError(f"Unsupported universe: {universe}")

    asof, new_items = await refresh_krx300(max_days=max_days)

    # --- 2) load old ---
    from db2.universe import get_universe_latest  # ✅ db2에 구현돼있다고 가정
    old_doc = await get_universe_latest(db, universe=universe)
    old_items = _payload_to_items(old_doc)

    # --- 3) diff ---
    d = diff_universe(universe=universe, asof=asof, new_items=new_items, old_items=old_items)

    # --- 4) save ---
    from db2.universe import upsert_universe_latest, insert_universe_snapshot  # ✅ 가정
    await upsert_universe_latest(db, universe=universe, items=_items_to_payload(new_items), asof=asof)
    if snapshot:
        await insert_universe_snapshot(db, universe=universe, items=_items_to_payload(new_items), asof=asof)

    return d


async def apply_removed_to_nfs(
    db: AsyncDatabase,
    *,
    removed_codes: Iterable[str],
) -> dict[str, int]:
    """
    removed codes를 nfs(latest/snapshots)에서 모두 삭제.
    """
    codes = [str(c).strip() for c in removed_codes if c and str(c).strip()]
    if not codes:
        return {"latest_deleted": 0, "snapshots_deleted": 0}

    # 너가 db2.nfs에 추가한 “명확한 의도 API”로 맞추는 걸 추천
    # 예: delete_codes_from_all_endpoints(db, codes)
    try:
        from db2.nfs import delete_codes_from_all_endpoints  # ✅ 네가 추가했다고 가정
        return await delete_codes_from_all_endpoints(db, codes=codes)
    except Exception:
        # fallback: 이미 있는 delete_codes_from_nfs(endpoint=None) 사용
        from db2.nfs import delete_codes_from_nfs
        return await delete_codes_from_nfs(db, codes=codes, endpoint=None)  # type: ignore[arg-type]