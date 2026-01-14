from __future__ import annotations

from typing import Any

from excel_orm import Column


class RowBase:
    __columns__: list[Column[Any]]

    def __init__(self, **kwargs: Any) -> None:
        self._values: dict[str, Any] = {}

        for col in getattr(self, "__columns__", []):
            if col.name is None:
                continue
            self._values[col.name] = col.spec.default

        for k, v in kwargs.items():
            setattr(self, k, v)
