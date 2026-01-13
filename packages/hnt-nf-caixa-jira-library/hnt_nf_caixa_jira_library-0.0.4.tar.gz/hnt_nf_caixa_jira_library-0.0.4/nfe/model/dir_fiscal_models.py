from __future__ import annotations

import json
import os
from typing import List, Optional

from pydantic import BaseModel


class DirFiscal(BaseModel):
    cnpj: str
    empresa: Optional[str] = None
    cd: Optional[str] = None
    tipo_nf: Optional[str] = None
    dir_fiscal: Optional[str] = None
    tipo_item_nf: Optional[str] = None


class DirFiscalRepository:
    """Repository for DirFiscal records.

    Similar pattern to CFOPRepository: load from file, list, filter and get by cnpj.
    """

    def __init__(self, items: Optional[List[DirFiscal]] = None) -> None:
        self._items = items or []

    @classmethod
    def load_from_file(cls, path: Optional[str]) -> "DirFiscalRepository":
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "dir_fiscal.json")
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        return cls.from_list(data)

    @classmethod
    def load_default(cls) -> "DirFiscalRepository":
        return cls.load_from_file(None)

    @classmethod
    def from_list(cls, data: List[dict]) -> "DirFiscalRepository":
        items = [DirFiscal(**d) for d in data]
        return cls(items)

    def get_all(self) -> List[DirFiscal]:
        return list(self._items)

    def get_by_cnpj(self, cnpj: str) -> Optional[DirFiscal]:
        for it in self._items:
            if it.cnpj == cnpj:
                return it
        return None

    def filter(self, **kwargs) -> List[DirFiscal]:
        results = self._items
        for key, value in kwargs.items():
            results = [r for r in results if getattr(r, key, None) == value]
        return results
