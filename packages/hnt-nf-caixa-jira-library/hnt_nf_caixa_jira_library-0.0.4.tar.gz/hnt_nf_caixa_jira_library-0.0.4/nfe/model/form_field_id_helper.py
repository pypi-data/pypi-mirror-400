# -*- coding: utf-8 -*-
"""
Helper para localizar o id (chave) do campo no arquivo de form (form.json)
dado o `questionKey`.

Uso:
    from nfe.model.form_field_id_helper import FormFieldIdHelper
    helper = FormFieldIdHelper("devdata/json/form.json")
    helper.get_field_id('run_process_id')  # => '13'
"""
import json
from typing import Any, Dict, Optional, Union


class FormFieldIdHelper:
    """Recebe um dict (JSON já carregado) ou caminho para o arquivo JSON.

    Métodos:
    - get_field_id(question_key) -> Optional[str]
    """

    def __init__(self, data: Union[str, Dict[str, Any]]):
        if isinstance(data, str):
            with open(data, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)
        elif isinstance(data, dict):
            self._data = data
        else:
            raise TypeError("data must be a file path or a dict")

        self._questions = self._extract_questions()

    def _extract_questions(self) -> Dict[str, Any]:
        design = self._data.get("design", {}) if isinstance(self._data, dict) else {}
        return design.get("questions", {})

    def get_field_id(self, question_key: str) -> Optional[str]:
        """Retorna a chave (id) do campo que contém `questionKey`.

        Exemplo: `get_field_id('run_process_id')` retorna `'13'`.
        Retorna `None` se não encontrar.
        """
        for field_id, info in self._questions.items():
            if isinstance(info, dict) and info.get("questionKey") == question_key:
                return str(field_id)
        return None
