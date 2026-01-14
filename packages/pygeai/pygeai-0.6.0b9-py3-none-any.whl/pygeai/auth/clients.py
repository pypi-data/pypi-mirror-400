from pygeai import logger
from pygeai.auth.endpoints import GET_USER_PROFILE_INFO, GET_OAUTH2_ACCESS_TOKEN, \
    CREATE_PROJECT_API_TOKEN_V2, DELETE_PROJECT_API_TOKEN_V2, UPDATE_PROJECT_API_TOKEN_V2, GET_PROJECT_API_TOKEN_V2
from pygeai.core.base.clients import BaseClient
from pygeai.core.common.exceptions import InvalidAPIResponseException, APIResponseError
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response


class AuthClient(BaseClient):

    def get_oauth2_access_token(
            self,
            client_id: str,
            username: str,
            password: str,
            scope: str = "gam_user_data gam_user_roles"
    ) -> dict:
        """
        Retrieves the list of projects that the user is authorized to access within a specific organization.

        :param client_id: str - The client identifier provided by Globant
        :param username: str - Username for authentication
        :param password: str - Password for authentication
        :param scope: str - Space-separated list of requested scopes
        :return: dict - The API response containing the list of authorized projects in JSON format.
        """
        response = self.api_service.get(
            endpoint=GET_OAUTH2_ACCESS_TOKEN,
            params={
                "client_id": client_id,
                "scope": scope,
                "username": username,
                "password": password
            }
        )
        validate_status_code(response)
        return parse_json_response(response, "obtain Oauth2 access token")

    def get_user_profile_information(self, access_token: str) -> dict:
        """
        Get user profile information

        :param access_token: str - Token obtained in the POST to /oauth/access_token
        :return: dict - The API response containing the user profile information
        """
        self.api_service.token = access_token
        response = self.api_service.get(endpoint=GET_USER_PROFILE_INFO)
        validate_status_code(response)
        return parse_json_response(response, "retrieve user profile information")

    def create_project_api_token(
            self,
            project_id: str,
            name: str,
            description: str = None
    ) -> dict:
        """
        Creates a new API token for a project.

        :param project_id: str - The project identifier (required). Will be sent as header.
        :param name: str - The name of the API token (required).
        :param description: str - A description of the API token (optional).
        :return: dict - The API response containing the created API token details in JSON format.
        """
        headers = {"project-id": project_id}
        data = {"name": name}
        if description:
            data["description"] = description

        response = self.api_service.post(
            endpoint=CREATE_PROJECT_API_TOKEN_V2,
            data=data,
            headers=headers
        )
        validate_status_code(response)
        return parse_json_response(response, "create project API token")

    def delete_project_api_token(self, api_token_id: str) -> dict:
        """
        Revokes an API token by setting its status to "revoked".

        :param api_token_id: str - The unique identifier of the API token to delete (required).
        :return: dict - The API response confirming the deletion, in JSON format.
        """
        endpoint = DELETE_PROJECT_API_TOKEN_V2.format(id=api_token_id)
        response = self.api_service.delete(endpoint=endpoint)
        validate_status_code(response)
        return parse_json_response(response, "delete project API token", api_token_id=api_token_id)

    def update_project_api_token(
            self,
            api_token_id: str,
            description: str = None,
            status: str = None
    ) -> dict:
        """
        Updates an existing API token's description and/or status.

        :param api_token_id: str - The unique identifier of the API token to update (required).
        :param description: str - A new description for the API token (optional).
        :param status: str - The new status for the API token: 'active' or 'blocked' (optional).
        :return: dict - The API response containing the update result messages in JSON format.
        """
        endpoint = UPDATE_PROJECT_API_TOKEN_V2.format(id=api_token_id)
        data = {}
        if description is not None:
            data["description"] = description
        if status is not None:
            data["status"] = status

        response = self.api_service.put(
            endpoint=endpoint,
            data=data
        )
        validate_status_code(response)
        return parse_json_response(response, "update project API token", api_token_id=api_token_id)

    def get_project_api_token(self, api_token_id: str) -> dict:
        """
        Retrieves data for a specific project API token.

        :param api_token_id: str - The unique identifier of the API token (required).
        :return: dict - The API response containing the API token details in JSON format.
        """
        endpoint = GET_PROJECT_API_TOKEN_V2.format(id=api_token_id)
        response = self.api_service.get(endpoint=endpoint)
        validate_status_code(response)
        return parse_json_response(response, "get project API token", api_token_id=api_token_id)
