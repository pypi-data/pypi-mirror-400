from __future__ import annotations

import json
import os
from typing import List, Optional

from pydantic import BaseModel


class CFOP(BaseModel):
    cfop_nf: str
    descricao_operacao: Optional[str] = None
    cfop_sap: Optional[str] = None


class CFOPRepository:
    """Utility repository for CFOP objects.

    Provides convenience loaders and query methods.
    """

    def __init__(self, cfops: Optional[List[CFOP]] = None) -> None:
        # allow empty construction so callers can use instance methods like
        # `CFOPRepository().load_default()` in tests
        self._cfops = cfops or []

    @classmethod
    def load_from_file(cls, path: Optional[str]) -> "CFOPRepository":
        """Load CFOP list from a JSON file and return a repository."""
        if path is None:
            # default to cfops.json located next to this module
            path = os.path.join(os.path.dirname(__file__), "cfops.json")
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        return cls.from_list(data)

    @classmethod
    def load_default(cls) -> "CFOPRepository":
        """Load the `cfops.json` file located in the same directory as this module."""
        return cls.load_from_file(None)

    @classmethod
    def from_list(cls, data: List[dict]) -> "CFOPRepository":
        """Create repository from a raw list of dicts."""
        cfops = [CFOP(**d) for d in data]
        return cls(cfops)

    def get_all(self) -> List[CFOP]:
        """Return all CFOP objects."""
        return list(self._cfops)

    def get_by_cfop_nf(self, cfop_nf: str) -> Optional[CFOP]:
        """Return first CFOP that matches `cfop_nf` (exact match).

        If multiple entries exist, returns the first occurrence.
        """
        for c in self._cfops:
            if c.cfop_nf == cfop_nf:
                return c
        return None

    def filter(self, **kwargs) -> List[CFOP]:
        """Simple filter by fields (supports equality only)."""
        results = self._cfops
        for key, value in kwargs.items():
            results = [r for r in results if getattr(r, key, None) == value]
        return results
