from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

from .nfe_models import NFeBaseModel

class FornecedorMaterial(NFeBaseModel):
    id: int
    nro_documento_fornecedor: str
    tipo_documento_fornecedor: str
    nome_fornecedor: str
    cod_material_fornecedor: str
    descricao_manterial: str
    cod_material_sap: str
    medida: Optional[str] = None
    multiplo: Optional[Any] = None

class FornecedorCaixa(NFeBaseModel):
    id: int
    sap_cod_fornecedor: str
    nome_fornecedor: str
    nro_documento: str
    tipo_documento: str
    tipo_fornecedor: str

__all__ = ["FornecedorMaterial", "FornecedorCaixa"]
