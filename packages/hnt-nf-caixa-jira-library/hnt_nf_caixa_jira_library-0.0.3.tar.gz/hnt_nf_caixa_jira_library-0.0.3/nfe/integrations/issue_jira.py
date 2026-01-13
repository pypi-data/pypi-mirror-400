import json
import requests
import logging

from nfe.constants import API_HEADERS, API_ISSUE_URL, JIRA_AUTH
logger = logging.getLogger(__name__)
class IssueJira:
    def get_issue(self, issue_key):
        issue = self._get_issue_data(issue_key)
        return issue

    def _get_issue_data(self, issue_key):
        try:
            request = requests.get(
                f"{API_ISSUE_URL}/issue/{issue_key}",
                headers=API_HEADERS,
                auth=JIRA_AUTH,
            )
            request.raise_for_status()
            data = request.json()

            return data
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber dados da issue:\n{e}")
        
    def _get_issue_fields(self, issue):

        jira_fields = issue.get('fields')
        return jira_fields
            
class CommentJira:
    def add_payload_comment(self, issue_key, payload):
        try:
            res = requests.post(
                f"{API_ISSUE_URL}/issue/{issue_key}/comment",
                auth=JIRA_AUTH,
                headers=API_HEADERS,
                data=json.dumps(payload),
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao enviar comentario para issue:\n{e}")

    def add_comment(self, issue_key, comment):

        self._add_comment(issue_key, comment)
        pass

    def _add_comment(self, issue_key, message):

        try:
            payload = json.dumps(
                {
                    "body": {
                        "content": [
                            {
                                "content": [
                                    {
                                        "type": "emoji",
                                        "attrs": {
                                            "shortName": ":robot:",
                                            "id": "1f916",
                                            "text": "🤖",
                                        },
                                    },
                                    {"text": f" {message}", "type": "text"},
                                ],
                                "type": "paragraph",
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    }
                }
            )
            res = requests.post(
                f"{API_ISSUE_URL}/issue/{issue_key}/comment",
                auth=JIRA_AUTH,
                headers=API_HEADERS,
                data=payload,
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao enviar comentario para issue:\n{e}")
        