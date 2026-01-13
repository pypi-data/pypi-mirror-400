import requests

from nfe.constants import API_ATLASSIAN_HEADERS, API_ATLASSIAN_HEADERS, API_FORM_URL, CLOUD_ID, JIRA_AUTH

class FormJira:
    def put_save_form_answers(self, answers, issue_key, form_template):
        forms_from_issue = self._get_forms_from_issue(issue_key)
        form_id = self._get_form_id_data(forms_from_issue, form_template)
        self._save_form_answers(answers, issue_key, form_id)

    def get_form_answers(self, issue_key, form_template):
        form_answers = self._get_form_answers(issue_key, form_template)
        # form_fields = self._get_form_fields_data(form_data)
        return form_answers
    
    def get_form_fields(self, issue_key, form_template):

        form_data = self.get_form_data(issue_key, form_template)
        form_fields = self._get_form_fields_data(form_data)
        return form_fields
    
    def get_form_id(self, issue_key, form_template):

        forms_from_issue = self._get_forms_from_issue(issue_key)
        form_id = self._get_form_id_data(forms_from_issue, form_template)

        return form_id
    
    def get_form_jira_status(self, issue_key, form_template):        
        form_data = self.get_form_data(issue_key, form_template)
        return self._get_form_jira_status(form_data)

    def get_form_jira_keys(self, issue_key, form_template):
        
        form_data = self.get_form_data(issue_key, form_template)
        form_keys = self._get_form_jira_keys(form_data)

        return form_keys

    def get_form_data(self, issue_key, form_template):

        forms_from_issue = self._get_forms_from_issue(issue_key)
        form_id = self._get_form_id_data(forms_from_issue, form_template)
        form_data = self._get_form(form_id, issue_key)

        return form_data
    def _get_form_answers(self, issue_key, form_template):

        forms_from_issue = self._get_forms_from_issue(issue_key)
        form_id = self._get_form_id_data(forms_from_issue, form_template)
        form_answers = self._get_form_format_answers(form_id, issue_key)

        return form_answers
    def _get_forms_from_issue(self, issue_key):

        try:
            request = requests.get(
                f"{API_FORM_URL}/{CLOUD_ID}/issue/{issue_key}/form",
                headers=API_ATLASSIAN_HEADERS,
                auth=JIRA_AUTH,
            )
            request.raise_for_status()
            data = request.json()
            
            return data
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber formulario da issue:\n{e}")
        
    def _get_form_id_data(self, data, form_template):
        form_id = None    
        for form in data:
            if form.get("formTemplate")['id'] == form_template:
                form_id = form.get("id")
        if form_id is None:
            raise Exception(f"Formulario não encontrado, Template: {form_template}")
        return  form_id
    
    def _get_form_format_answers(self, form_id, issue_key):
        try:
            request = requests.get(
                f"{API_FORM_URL}/{CLOUD_ID}/issue/{issue_key}/form/{form_id}/format/answers",
                headers=API_ATLASSIAN_HEADERS,
                auth=JIRA_AUTH,
            )
            request.raise_for_status()
            data = request.json()

            return data
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao capturar formulario:\n{e}")
    def _get_form(self, form_id, issue_key):

        try:
            request = requests.get(
                f"{API_FORM_URL}/{CLOUD_ID}/issue/{issue_key}/form/{form_id}",
                headers=API_ATLASSIAN_HEADERS,
                auth=JIRA_AUTH,
            )
            request.raise_for_status()
            data = request.json()

            return data
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao capturar formulario:\n{e}")
        
    def _get_form_fields_data(self, data):

        fields_json = {}

        fields_values = data.get('state')['answers']
        fields_root = data.get('design')['questions']
        
        for root in fields_root:

            field_name = fields_root[root].get('questionKey')
            if fields_values.get(root) is not None:
                if "choices" in list(fields_values.get(root).keys()):
                    if field_name == 'codigo_imposto':
                        field_index = fields_values.get(root)['choices'][0]
                        field_value = fields_root[root]['choices'][int(field_index) - 1]['label'].split(' ', 1)[0]
                    else:
                        field_value = fields_values.get(root)['choices']

                else:
                    field_index = list(fields_values.get(root).keys())[0]
                    field_value = fields_values.get(root)[field_index]
            else: 
                field_value = None

            fields_json[field_name] = field_value

        return fields_json
    
    def _get_form_jira_status(self, data):
        return data.get('state')['status']
    
    def _get_form_jira_keys(self, data):
        field_keys = {}
        fields_root = data.get('design')['questions']

        for root in fields_root:

            field_name = fields_root[root].get('questionKey')
            jira_key = fields_root[root].get('jiraField')
            field_keys[field_name] = jira_key

        return field_keys

    def update_jira_form(self, issue, data):

        answers_schema = {
            "1":"cod_nota_pedido",
            "4":"cod_fatura",
            "5":"status_liberacao",
            "6":"data_liberacao",
            "7":"cod_miro"
        }

        answers_json = {}

        for answer in answers_schema:
            answer_label = answers_schema[answer]
            if answer_label in data:
                answers_json[answer] = {"text": data[answer_label]}

        answers = { "answers" : answers_json }

        self._save_form_answers(answers, issue["issue_id"], issue["form_id"])

        pass
    
    def _save_form_answers(self, answers, issue_id, form_id):

        try:
            requests.put(
                f"{API_FORM_URL}/{CLOUD_ID}/issue/{issue_id}/form/{form_id}",
                headers = API_ATLASSIAN_HEADERS,
                auth = JIRA_AUTH,
                json = answers,
            )

            pass

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber anexo Jira:\n{e}")