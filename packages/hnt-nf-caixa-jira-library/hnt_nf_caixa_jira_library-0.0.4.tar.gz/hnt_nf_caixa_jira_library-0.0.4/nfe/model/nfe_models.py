
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import Annotated


# -------------------------
# Tipos auxiliares
# -------------------------
CPFType = Annotated[str, Field(pattern=r"^\d{11}$")]
CNPJType = Annotated[str, Field(pattern=r"^\d{14}$")]
UFType = Annotated[str, Field(min_length=2, max_length=2)]
CFOP = Annotated[str, Field(pattern=r"^\d{4}$")]


class NFeBaseModel(BaseModel):
    """
    Base comum:
    - extra='allow' para tolerar campos adicionais do layout
    - validate_assignment=True ajuda em mutações (se você permitir)
    """
    model_config = ConfigDict(extra="allow", validate_assignment=True)


# -------------------------
# Blocos principais
# -------------------------
class Ide(NFeBaseModel):
    cUF: str
    cNF: str
    natOp: str
    mod: str
    serie: str
    nNF: str
    dhEmi: datetime
    dhSaiEnt: Optional[datetime] = None
    tpNF: str
    idDest: str
    cMunFG: str
    tpImp: str
    tpEmis: str
    cDV: str
    tpAmb: str
    finNFe: str
    indFinal: str
    indPres: str
    procEmi: str
    verProc: str


class Endereco(NFeBaseModel):
    xLgr: str
    nro: str
    xBairro: str
    cMun: str
    xMun: str
    UF: UFType
    CEP: str
    cPais: str
    xPais: str
    fone: Optional[str] = None


class Emit(NFeBaseModel):
    CPF: Optional[CPFType] = None
    CNPJ: Optional[CNPJType] = None
    xNome: str
    xFant: Optional[str] = None
    enderEmit: Endereco
    IE: Optional[str] = None
    CRT: Optional[str] = None

    @property
    def nro_documento(self) -> Optional[str]:
        """Retorna o número do documento do emitente: `CNPJ` ou `CPF`.

        - Se ambos estiverem presentes, levanta `ValueError` (inconsistência).
        - Se nenhum estiver presente, retorna `None`.
        """
        if self.CNPJ and self.CPF:
            raise ValueError("Ambos CNPJ e CPF presentes — documento ambíguo")
        return self.CNPJ or self.CPF


class Dest(NFeBaseModel):
    CNPJ: CNPJType
    xNome: str
    enderDest: Endereco
    indIEDest: Optional[str] = None
    IE: Optional[str] = None
    email: Optional[str] = None


# -------------------------
# Detalhe de itens (det)
# -------------------------
class Prod(NFeBaseModel):
    cProd: str
    cEAN: Optional[str] = None
    xProd: str
    NCM: Optional[str] = None
    cBenef: Optional[str] = None
    CFOP: CFOP
    uCom: Optional[str] = None
    qCom: Optional[Decimal] = None
    vUnCom: Optional[Decimal] = None
    vProd: Optional[Decimal] = None
    cEANTrib: Optional[str] = None
    uTrib: Optional[str] = None
    qTrib: Optional[Decimal] = None
    vUnTrib: Optional[Decimal] = None
    indTot: Optional[str] = None


class Icms40(NFeBaseModel):
    orig: str
    CST: str


class ICMS(NFeBaseModel):
    # No seu JSON aparece ICMS40 dentro de ICMS. [3](blob:https://outlook.office.com/b148daff-01b3-45d7-be4c-5d13055c6fb1)
    ICMS40: Optional[Icms40] = None


class PisOutr(NFeBaseModel):
    CST: str
    vBC: Optional[Decimal] = None
    pPIS: Optional[Decimal] = None
    vPIS: Optional[Decimal] = None


class PIS(NFeBaseModel):
    # No seu JSON aparece PISOutr. [3](blob:https://outlook.office.com/b148daff-01b3-45d7-be4c-5d13055c6fb1)
    PISOutr: Optional[PisOutr] = None


class CofinsOutr(NFeBaseModel):
    CST: str
    vBC: Optional[Decimal] = None
    pCOFINS: Optional[Decimal] = None
    vCOFINS: Optional[Decimal] = None


class COFINS(NFeBaseModel):
    # No seu JSON aparece COFINSOutr. [3](blob:https://outlook.office.com/b148daff-01b3-45d7-be4c-5d13055c6fb1)
    COFINSOutr: Optional[CofinsOutr] = None


class Imposto(NFeBaseModel):
    ICMS: ICMS
    PIS: PIS
    COFINS: COFINS


class DetItem(NFeBaseModel):
    # No seu JSON, cada item tem "prod" e "imposto". [1](blob:https://outlook.office.com/d83ba011-1643-4716-ac5a-bb164e6807a2)[3](blob:https://outlook.office.com/b148daff-01b3-45d7-be4c-5d13055c6fb1)
    prod: Prod
    imposto: Imposto


# -------------------------
# Total, Transporte, Pagamento, Adicionais, Resp. Técnico
# -------------------------
class ICMSTot(NFeBaseModel):
    # No seu JSON, estes valores vêm como strings numéricas. [4](blob:https://outlook.office.com/61724482-0844-4aa3-9fbd-4206975fe942)
    vBC: Decimal
    vICMS: Decimal
    vICMSDeson: Decimal
    vFCP: Decimal
    vBCST: Decimal
    vST: Decimal
    vFCPST: Decimal
    vFCPSTRet: Decimal
    vProd: Decimal
    vFrete: Decimal
    vSeg: Decimal
    vDesc: Decimal
    vII: Decimal
    vIPI: Decimal
    vIPIDevol: Decimal
    vPIS: Decimal
    vCOFINS: Decimal
    vOutro: Decimal
    vNF: Decimal


class Total(NFeBaseModel):
    ICMSTot: ICMSTot


class Transporta(NFeBaseModel):
    CNPJ: CNPJType
    xNome: str
    IE: Optional[str] = None
    xEnder: Optional[str] = None
    xMun: Optional[str] = None
    UF: Optional[UFType] = None


class Vol(NFeBaseModel):
    qVol: Optional[Decimal] = None
    esp: Optional[str] = None
    pesoL: Optional[Decimal] = None
    pesoB: Optional[Decimal] = None


class Transp(NFeBaseModel):
    modFrete: str
    transporta: Optional[Transporta] = None
    vol: Optional[Vol] = None


class DetPag(NFeBaseModel):
    tPag: str
    vPag: Decimal


class Pag(NFeBaseModel):
    # No seu JSON, detPag vem como dict (não lista). [4](blob:https://outlook.office.com/61724482-0844-4aa3-9fbd-4206975fe942)
    detPag: DetPag


class InfAdic(NFeBaseModel):
    infAdFisco: Optional[str] = None


class InfRespTec(NFeBaseModel):
    CNPJ: CNPJType
    xContato: Optional[str] = None
    email: Optional[str] = None
    fone: Optional[str] = None


# -------------------------
# Signature (opcional, mas presente no seu JSON)
# -------------------------
class SignatureModel(NFeBaseModel):
    # Estrutura existe: SignedInfo, SignatureValue, KeyInfo. [2](blob:https://outlook.office.com/971e170d-42b4-44f4-9210-7ffbae09d16f)
    SignedInfo: Optional[Dict[str, Any]] = None
    SignatureValue: Optional[str] = None
    KeyInfo: Optional[Dict[str, Any]] = None


# -------------------------
# NFe / ProtNFe
# -------------------------
class InfNFe(NFeBaseModel):
    # Estrutura conforme seu arquivo: ide/emit/dest/det/total/transp/pag/infAdic/infRespTec. [1](blob:https://outlook.office.com/d83ba011-1643-4716-ac5a-bb164e6807a2)[4](blob:https://outlook.office.com/61724482-0844-4aa3-9fbd-4206975fe942)
    ide: Ide
    emit: Emit
    dest: Dest
    det: List[DetItem]
    total: Total
    transp: Transp
    pag: Pag
    infAdic: Optional[InfAdic] = None
    infRespTec: Optional[InfRespTec] = None

    @field_validator("det", mode="before")
    def ensure_det_list(cls, v):
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v


class NFe(NFeBaseModel):
    infNFe: InfNFe
    Signature: Optional[SignatureModel] = None  # presente no seu JSON. [2](blob:https://outlook.office.com/971e170d-42b4-44f4-9210-7ffbae09d16f)


class InfProt(NFeBaseModel):
    tpAmb: str
    verAplic: str
    chNFe: str
    dhRecbto: datetime
    nProt: str
    digVal: str
    cStat: str
    xMotivo: str


class ProtNFe(NFeBaseModel):
    infProt: InfProt


class NFeEnvelope(NFeBaseModel):
    # Top-level: "NFe" e "protNFe". [5](placeholder-4)[1](blob:https://outlook.office.com/d83ba011-1643-4716-ac5a-bb164e6807a2)
    NFe: NFe
    protNFe: ProtNFe
