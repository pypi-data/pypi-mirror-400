
from pygeai import logger
from pygeai.core.base.clients import BaseClient
from pygeai.core.common.exceptions import InvalidAPIResponseException
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response
from pygeai.health.endpoints import STATUS_CHECK_V1


class HealthClient(BaseClient):

    def check_api_status(self) -> dict:
        """
        Checks the status of the API.

        :return: dict - The API response as a JSON object containing details about the API status.
        If the response cannot be parsed as JSON, returns the raw response text.
        """
        endpoint = STATUS_CHECK_V1
        response = self.api_service.get(
            endpoint=endpoint
        )
        validate_status_code(response)
        return parse_json_response(response, "check API status")
