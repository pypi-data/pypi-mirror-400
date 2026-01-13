import logging
import locale
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from nfe.constants import MODALID_FRET_9, NF_CAIXA_FORM_TEMPLATE_ID
from nfe.integrations.form_jira import FormJira
from nfe.model.cfop_models import CFOPRepository
from nfe.model.dir_fiscal_models import DirFiscalRepository
from nfe.model.form_nf_caixa_models import FormNFCaixa
from nfe.integrations.n8n_domain import N8NDomain

logger = logging.getLogger(__name__)
from dotenv import load_dotenv

from nfe.HntException import HntException
from nfe.model.nfe_models import NFeEnvelope
from nfe.model.nfe_caixa_models import NFeCaixaEnvelope


class NFeCaixa:
    def __init__(self) -> None:
        try:
            locale.setlocale(locale.LC_ALL, ("pt_BR.UTF-8"))
        except Exception:
            logger.debug("pt_BR locale not available; continuing with default")
        load_dotenv()

    def build(self, issue_key, sefaz) -> NFeCaixaEnvelope:
        """Build and return a validated `NFeCaixaEnvelope` from input payload.

        Applies supplier selection rules and enriches items from fornecedores_material.
        Raises `HntException` on ambiguous or missing supplier rules.
        """
        nfe_env = NFeEnvelope.model_validate(sefaz)
        # supplier rules
        emit = nfe_env.NFe.infNFe.emit
        dest = nfe_env.NFe.infNFe.dest
        fornecedores_caixa = N8NDomain().get_fornecedor_caixa(nro_documento=emit.nro_documento)
        nfCaixaForm = FormNFCaixa.from_jira(issue_key, NF_CAIXA_FORM_TEMPLATE_ID)

        fornecedor_caixa = None
        if len(fornecedores_caixa) == 1:
            fornecedor_caixa = fornecedores_caixa[0]
        elif len(fornecedores_caixa) > 1 and nfCaixaForm.sap_cod_fornecedor is not None:
            fornecedor_caixa = next(
                (f for f in fornecedores_caixa if str(f.sap_cod_fornecedor) == str(nfCaixaForm.sap_cod_fornecedor)),
                None,
            )

        if fornecedor_caixa is None:
            raise HntException(
                f"multiple fornecedores_caixa found and form.sap_cod_fornecedor {nfCaixaForm.sap_cod_fornecedor} did not match any"
            )

        itens: List[Dict[str, Any]] = []
        cfopRepository = CFOPRepository().load_default()
        dirFiscalRepository = DirFiscalRepository.load_default()

        for det in nfe_env.NFe.infNFe.det:
            prod = det.prod
            fornecedor_material = N8NDomain().get_fornecedor_material(
                nro_documento=emit.nro_documento,
                cod_material_fornecedor=prod.cProd)
            cfop = cfopRepository.get_by_cfop_nf(cfop_nf=prod.CFOP)
            dirFiscal = dirFiscalRepository.get_by_cnpj(cnpj=dest.CNPJ)
            item = {
                "cod_produto": prod.cProd,
                "tipo": dirFiscal.tipo_item_nf,
                "nome_produto": prod.xProd,
                "cod_material_sap": fornecedor_material.cod_material_sap,
                "centro": dirFiscal.cd,
                "quantidade": self._fmt_number(prod.qCom),
                "unidade_medida": fornecedor_material.medida,
                "preco": self._fmt_number(prod.vUnCom),
                "valor_produto": self._fmt_number(prod.vProd),
                "cfop": cfop.cfop_sap,
                "dir_fiscal": dirFiscal.dir_fiscal,
            }
            itens.append(item)

        ide = nfe_env.NFe.infNFe.ide
        prot = nfe_env.protNFe.infProt
        

        data_emissao = None
        hora_emissao = None
        try:
            if isinstance(ide.dhEmi, datetime):
                data_emissao = ide.dhEmi.strftime("%d.%m.%Y")
                hora_emissao = ide.dhEmi.strftime("%H:%M:%S")
        except Exception:
            pass
        data = {
            "categoria_nf": fornecedor_caixa.tipo_fornecedor,
            "empresa": dirFiscal.empresa,
            "local_negocio": dirFiscal.cd,
            "funcao_parceiro": "LF",
            "sap_cod_fornecedor": fornecedor_caixa.sap_cod_fornecedor,
            "nro_nf": ide.nNF,
            "serie_nf": ide.serie,
            "data_emissao": data_emissao,
            "itens": itens,
            "dados_nfe": {
                "tipo_emissao":ide.tpEmis,
                "nro_aleatorio": ide.cNF,
                "digito_verificador": ide.cDV,
                "nro_log": prot.nProt,
                "data_emissao": data_emissao,
                "hora_emissao": hora_emissao,
                "modalid_fret": MODALID_FRET_9,
            },
        }

        # validate with pydantic model and return
        try:
            envelope = NFeCaixaEnvelope.model_validate(data)
        except Exception as e:
            raise HntException("failed to validate NFeCaixaEnvelope", cause=e)

        return envelope

    def _fmt_number(self, value: Optional[Any]) -> Optional[str]:
        if value is None:
            return None
        s = str(value)
        try:
            f = float(s)
        except Exception:
            return s
        if f.is_integer():
            return str(int(f))
        out = ("%f" % f).rstrip("0").rstrip(".")
        return out
