from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .nfe_models import NFeBaseModel


class FormField(NFeBaseModel):
    label: str
    fieldKey: str
    answer: Optional[str] = None


class FormAutomacao(NFeBaseModel):
    nro_documento_nota_fiscal: Optional[str] = None
    run_process_id: Optional[str] = None

    @classmethod
    def builder_from_list(cls, items: List[Dict[str, Any]]) -> "FormAutomacao":
        """Constroi uma instância de `FormAutomacao` a partir da lista de respostas do formulário.

        Espera `items` no formato do arquivo `form_test_nfe_caixa_automacao.json` —
        uma lista de objetos com `fieldKey`/`answer`.
        Strings vazias são convertidas para `None`.
        """
        data: Dict[str, Optional[str]] = {}
        for item in items:
            key = item.get("fieldKey")
            if key is None:
                continue
            ans = item.get("answer")
            if isinstance(ans, str) and ans.strip() == "":
                ans = None
            data[key] = ans

        # Filtra apenas os campos conhecidos pelo modelo
        allowed = {k: data.get(k) for k in cls.model_fields.keys()}
        return cls.model_validate(allowed)

    @classmethod
    def builder_from_file(cls, path: str) -> "FormAutomacao":
        """Lê o JSON do `path` e chama `builder_from_list`.
        """
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        return cls.builder_from_list(items)

    @classmethod
    def from_jira(
        cls, issue_key: str, form_template: str, form_jira: Optional[object] = None
    ) -> "FormAutomacao":
        """Factory that builds a `FormAutomacao` directly from a Jira form.

        This is a convenience method used in tests and higher-level code. A
        `FormJira` instance may be provided for easier testing; otherwise a new
        instance will be created.
        """
        if form_jira is None:
            from nfe.integrations.form_jira import FormJira

            form_jira = FormJira()

        form_answers = form_jira.get_form_answers(issue_key, form_template)
        return cls.builder_from_list(form_answers)


__all__ = ["FormField", "FormAutomacao"]
