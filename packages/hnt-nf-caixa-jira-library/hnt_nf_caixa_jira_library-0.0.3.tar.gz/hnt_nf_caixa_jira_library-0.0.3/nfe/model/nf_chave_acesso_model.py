
from typing import Any, Dict
from pydantic import BaseModel, ValidationError
from pydantic import field_validator
from typing_extensions import Annotated
from pydantic import StringConstraints


# Define o tipo: string numérica com exatamente 44 caracteres
ChaveAcesso = Annotated[
    str,
    StringConstraints(
        min_length=44,
        max_length=44,
        pattern=r'^\d{44}$'
    )
]


class NFChaveAcesso(BaseModel):
    """
    Modelo Pydantic para chave de acesso de NF-e/NFC-e.

    - Obrigatória
    - Somente dígitos (0-9)
    - Tamanho exatamente 44
    """
    chave_acesso: ChaveAcesso

    @classmethod
    def from_issue(cls, issue: Dict[str, Any]) -> "NFChaveAcesso":
        """
        Cria uma instância a partir de um dicionário no formato do retorno do Jira:
        issue = IssueJira().get_issue(issue_key)
        chave_acesso = issue['fields']['summary']
        """
        try:
            summary = issue["fields"]["summary"]
        except (KeyError, TypeError):
            raise ValueError(
                "Estrutura da issue inválida: esperava issue['fields']['summary']."
            )

        # Normalização simples (remover espaços em volta)
        if isinstance(summary, str):
            summary = summary.strip()
        else:
            raise ValueError("O campo 'summary' deve ser uma string.")

        # Usa a validação do próprio modelo
        return cls(chave_acesso=summary)

    # (Opcional) Validação adicional/normalização antes das restrições de tipo
    @field_validator("chave_acesso", mode="before")
    def somente_digitos_e_strip(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError("chave_acesso deve ser uma string.")
        v = v.strip()
        # Se vier com espaços, pontos ou hífens, remova-os (caso queira tolerância)
        # Descomente se desejar:
        # v = "".join(ch for ch in v if ch.isdigit())
        return v
