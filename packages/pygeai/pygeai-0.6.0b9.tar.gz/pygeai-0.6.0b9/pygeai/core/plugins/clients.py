from typing import Optional, List, Dict

from pygeai import logger
from pygeai.core.base.clients import BaseClient
from pygeai.core.common.exceptions import InvalidAPIResponseException
from pygeai.core.plugins.endpoints import LIST_ASSISTANTS_PLUGINS_V1
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response


class PluginClient(BaseClient):
    """
    Client for interacting with plugin endpoints of the API.
    """

    def list_assistants(
        self,
        organization_id: str,
        project_id: str
    ) -> dict:
        params = {
            "organization": organization_id,
            "project": project_id,
        }

        response = self.api_service.get(
            endpoint=LIST_ASSISTANTS_PLUGINS_V1,
            params=params
        )
        validate_status_code(response)
        return parse_json_response(response, f"list assistants for organization {organization_id} and project {project_id}")

