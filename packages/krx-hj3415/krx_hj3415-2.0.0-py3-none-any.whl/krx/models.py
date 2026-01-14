# krx/models.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


@dataclass(frozen=True)
class CodeItem:
    code: str
    name: str
    asof: datetime
    market: str | None = None  # 확장 대비(예: KRX/KOSPI/KOSDAQ/NYSE/NASDAQ 등)


@dataclass(frozen=True)
class UniverseDiff:
    universe: str
    asof: datetime
    added: list[CodeItem]
    removed: list[CodeItem]
    kept_count: int

    @property
    def added_codes(self) -> list[str]:
        return [x.code for x in self.added]

    @property
    def removed_codes(self) -> list[str]:
        return [x.code for x in self.removed]


def _to_code_map(items: Iterable[CodeItem]) -> dict[str, CodeItem]:
    return {it.code: it for it in items}


def diff_universe(*, universe: str, asof: datetime, new_items: list[CodeItem], old_items: list[CodeItem]) -> UniverseDiff:
    new_map = _to_code_map(new_items)
    old_map = _to_code_map(old_items)

    added = [new_map[c] for c in sorted(new_map.keys() - old_map.keys())]
    removed = [old_map[c] for c in sorted(old_map.keys() - new_map.keys())]
    kept = len(new_map.keys() & old_map.keys())

    return UniverseDiff(
        universe=universe,
        asof=asof,
        added=added,
        removed=removed,
        kept_count=kept,
    )