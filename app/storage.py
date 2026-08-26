"""In-memory repositories. No real DB — keeps the demo dependency-free and
each test able to reset() to a clean slate."""

from __future__ import annotations

from itertools import count
from typing import Any


class InMemoryRepo:
    def __init__(self) -> None:
        self._items: dict[int, dict[str, Any]] = {}
        self._id_counter = count(1)

    def reset(self) -> None:
        self._items.clear()
        self._id_counter = count(1)

    def create(self, **fields: Any) -> dict[str, Any]:
        item_id = next(self._id_counter)
        record = {"id": item_id, **fields}
        self._items[item_id] = record
        return record

    def get(self, item_id: int) -> dict[str, Any] | None:
        return self._items.get(item_id)

    def list(self) -> list[dict[str, Any]]:
        return list(self._items.values())

    def update(self, item_id: int, **fields: Any) -> dict[str, Any] | None:
        record = self._items.get(item_id)
        if record is None:
            return None
        record.update(fields)
        return record

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None

    def find_one(self, **criteria: Any) -> dict[str, Any] | None:
        for record in self._items.values():
            if all(record.get(k) == v for k, v in criteria.items()):
                return record
        return None


users_repo = InMemoryRepo()
products_repo = InMemoryRepo()
orders_repo = InMemoryRepo()


def reset_all() -> None:
    users_repo.reset()
    products_repo.reset()
    orders_repo.reset()
