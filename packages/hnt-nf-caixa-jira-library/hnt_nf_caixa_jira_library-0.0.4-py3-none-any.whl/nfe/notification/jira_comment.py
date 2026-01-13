
from typing import List, Dict, Any

def identification_comment(data) -> Dict[str, Any]:
    """
    Equivalente ao identificationComment(data) do JS.
    Recebe `data` com a chave 'itens' e retorna o corpo ADF para comentário.
    """
    return identification_template(
        sap_cod_fornecedor=data.sap_cod_fornecedor,
        nro_nf=data.nro_nf,
        serie_nf=data.serie_nf,
        data_emissao=data.data_emissao,
        itens=data.itens,
    )


def identification_template(
    sap_cod_fornecedor: str,
    nro_nf: str,
    serie_nf: str,
    data_emissao: str,
    itens: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Equivalente ao identificationTemplate({...}) do JS.
    Monta o documento ADF com duas tabelas (identificação + itens), uma regra e um expand.
    """
    return {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                # Tabela de identificação
                {
                    "type": "table",
                    "attrs": {
                        "isNumberColumnEnabled": False,
                        "layout": "align-start",
                        "localId": "5ed23c0f-0cdf-4d53-85cb-95a8e579ab72",
                    },
                    "content": [
                        _row_kv("Fornecedor SAP", sap_cod_fornecedor),
                        _row_kv("N° NF", nro_nf),
                        _row_kv("N° Serie", serie_nf),
                        _row_kv("DATA DE EMISSÃO", data_emissao),
                    ],
                },
                # Tabela de itens
                {
                    "type": "table",
                    "attrs": {
                        "isNumberColumnEnabled": True,
                        "layout": "align-start",
                        "localId": "99239ae7-e88a-4294-9dd3-4930d28d13da",
                    },
                    "content": itens_table_content(itens),
                }
            ],
        }
    }


def _row_kv(label: str, value: str) -> Dict[str, Any]:
    """Linha de tabela com duas células: rótulo e valor (como no JS)."""
    return {
        "type": "tableRow",
        "content": [
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": label}],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": value}],
                    }
                ],
            },
        ],
    }


def itens_table_content(itens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Equivalente a itensTableContent(itens) do JS:
    - Prepend do cabeçalho
    - Uma linha por item
    """
    rows: List[Dict[str, Any]] = []
    rows.append(table_header())
    for item in itens:
        rows.append(table_row(item))
    return rows


def table_row(item) -> Dict[str, Any]:
    """
    Equivalente a tableRow(item) do JS:
    Gera uma linha com 7 colunas, onde a primeira é tableHeader (numeração/índice),
    e as demais são tableCell com os campos do item.
    """
    return {
        "type": "tableRow",
        "content": [
            # 1ª coluna: tableHeader com cod_produto (como no JS)
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": f"{item.cod_produto}"}],
                    }
                ],
            },
            # Demais colunas: tableCell
            _cell_text(f"{item.nome_produto}"),
            _cell_text(f"{item.cfop}"),
            _cell_text(f"{item.quantidade}"),
            _cell_text(f"{item.preco}"),
            _cell_text(f"{item.valor_produto}"),
            _cell_text(f"{item.cod_material_sap}"),
        ],
    }


def table_header() -> Dict[str, Any]:
    """
    Equivalente a tableHeader() do JS:
    Linha de cabeçalho (7 colunas) para a tabela de itens.
    """
    def th(text: str) -> Dict[str, Any]:
        return {
            "type": "tableHeader",
            "attrs": {},
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
        }

    return {
        "type": "tableRow",
        "content": [
            th("CÓDIGO"),
            th("DESCRIÇÃO DO PRODUTO"),
            th("CFOP"),
            th("QTDE"),
            th("VLR UNIT"),
            th("VLR TOTAL"),
            th("Material SAP"),
        ],
    }


def _cell_text(text: str) -> Dict[str, Any]:
    """Ajuda a montar uma célula de texto simples."""
    return {
        "type": "tableCell",
        "attrs": {},
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }



