from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import Field, field_validator

from nfe.notification.jira_comment import identification_comment

from .nfe_models import NFeBaseModel


class ItemCaixa(NFeBaseModel):
    cod_produto: str
    tipo: str
    nome_produto: str
    cod_material_sap: Optional[str] = None
    centro: Optional[str] = None
    quantidade: Decimal
    unidade_medida: Optional[str] = None
    preco: Decimal
    valor_produto: Decimal
    cfop: Optional[str] = None
    dir_fiscal: Optional[str] = None


class DadosNFeCaixa(NFeBaseModel):
    tipo_emissao: Optional[str] = None
    nro_aleatorio: Optional[str] = None
    digito_verificador: Optional[str] = None
    nro_log: Optional[str] = None
    data_emissao: Optional[str] = None
    hora_emissao: Optional[str] = None
    modalid_fret: Optional[str] = None


class NFeCaixaEnvelope(NFeBaseModel):
    categoria_nf: str
    empresa: str
    local_negocio: str
    funcao_parceiro: str
    sap_cod_fornecedor: str
    nro_nf: str
    serie_nf: Optional[str] = None
    data_emissao: Optional[str] = None
    itens: List[ItemCaixa]
    dados_nfe: DadosNFeCaixa

    @field_validator("itens", mode="before")
    def ensure_itens_list(cls, v):
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v

    def jira_comment(self):
        return identification_comment(self)