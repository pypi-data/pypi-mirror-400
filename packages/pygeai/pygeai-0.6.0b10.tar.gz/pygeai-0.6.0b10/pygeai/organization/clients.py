
from pygeai import logger
from pygeai.core.common.exceptions import InvalidAPIResponseException
from pygeai.organization.endpoints import GET_ASSISTANT_LIST_V1, GET_PROJECT_LIST_V1, GET_PROJECT_V1, \
    CREATE_PROJECT_V1, UPDATE_PROJECT_V1, DELETE_PROJECT_V1, GET_PROJECT_TOKENS_V1, GET_REQUEST_DATA_V1, \
    GET_MEMBERSHIPS_V2, GET_PROJECT_MEMBERSHIPS_V2, GET_PROJECT_ROLES_V2, GET_PROJECT_MEMBERS_V2, \
    GET_ORGANIZATION_MEMBERS_V2
from pygeai.core.base.clients import BaseClient
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response


class OrganizationClient(BaseClient):

    def get_assistant_list(
            self,
            detail: str = "summary"
    ) -> dict:
        """
        Retrieves a list of assistants with the specified level of detail.

        :param detail: str - The level of detail to include in the response. Possible values:
            - "summary": Provides a summarized list of assistants. (Default)
            - "full": Provides a detailed list of assistants. (Optional)
        :return: AssistantListResponse - The API response containing the list of assistants and the project.
        """
        response = self.api_service.get(endpoint=GET_ASSISTANT_LIST_V1, params={"detail": detail})
        validate_status_code(response)
        return parse_json_response(response, "get assistant list")

    def get_project_list(
            self,
            detail: str = "summary",
            name: str = None
    ) -> dict:
        """
        Retrieves a list of projects based on the specified level of detail and optional project name.

        :param detail: str - The level of detail to include in the response. Possible values:
            - "summary": Provides a summarized list of projects. (Default)
            - "full": Provides a detailed list of projects. (Optional)
        :param name: str - (Optional) Filters the project list by an exact project name match.
        :return: dict - The API response containing the list of projects in JSON format.
        """
        if detail and name:
            response = self.api_service.get(
                endpoint=GET_PROJECT_LIST_V1,
                params={
                    "detail": detail,
                    "name": name
                }
            )
        else:
            response = self.api_service.get(
                endpoint=GET_PROJECT_LIST_V1,
                params={
                    "detail": detail
                }
            )
        validate_status_code(response)
        return parse_json_response(response, "get project list")

    def get_project_data(
            self,
            project_id: str
    ) -> dict:
        """
        Retrieves detailed information about a specific project based on its unique project ID.

        :param project_id: str - The GUID of the project (required).
        :return: dict - The API response containing the project details in JSON format.
        """
        endpoint = GET_PROJECT_V1.format(id=project_id)
        response = self.api_service.get(
            endpoint=endpoint
        )
        validate_status_code(response)
        return parse_json_response(response, "get project data for ID", project_id=project_id)

    def create_project(
            self,
            name: str,
            email: str,
            description: str = None,
            usage_limit: dict = None
    ) -> dict:
        """
        Creates a new project with the provided details. Optionally, a usage limit can be specified.

        :param name: str - The name of the new project (required).
        :param email: str - The email address of the project administrator (required).
        :param description: str - A description of the new project (optional).
        :param usage_limit: dict - A dictionary specifying the usage limits for the project. If provided, it must include usage type and thresholds (optional).
        :return: dict - The API response with details of the created project in JSON format.
        """
        if usage_limit and any(usage_limit):
            response = self.api_service.post(
                endpoint=CREATE_PROJECT_V1,
                data={
                    "name": name,
                    "administratorUserEmail": email,
                    "description": description,
                    "usageLimit": usage_limit
                }
            )
        else:
            response = self.api_service.post(
                endpoint=CREATE_PROJECT_V1,
                data={
                    "name": name,
                    "administratorUserEmail": email,
                    "description": description
                }
            )
        validate_status_code(response)
        return parse_json_response(response, "create project with name", name=name)

    def update_project(
            self,
            project_id: str,
            name: str,
            description: str = None
    ) -> dict:
        """
        Updates an existing project with the provided details.

        :param project_id: str - The unique identifier (GUID) of the project to update (required).
        :param name: str - The new name for the project (required).
        :param description: str - A new description for the project (optional).
        :return: dict - The API response containing the updated project details in JSON format.
        """
        endpoint = UPDATE_PROJECT_V1.format(id=project_id)
        response = self.api_service.put(
            endpoint=endpoint,
            data={
                "name": name,
                "description": description
            }
        )
        validate_status_code(response)
        return parse_json_response(response, "update project with ID", project_id=project_id)

    def delete_project(
            self,
            project_id
    ) -> dict:
        """
        Deletes an existing project using its unique identifier.

        :param project_id: str - The unique identifier (GUID) of the project to delete (required).
        :return: dict - The API response confirming the deletion of the project, in JSON format.
        """
        endpoint = DELETE_PROJECT_V1.format(id=project_id)
        response = self.api_service.delete(endpoint=endpoint)
        validate_status_code(response)
        return parse_json_response(response, "delete project with ID", project_id=project_id)

    def get_project_tokens(
            self,
            project_id
    ) -> dict:
        """
        Retrieves the tokens associated with a specific project using its unique identifier.

        :param project_id: str - The unique identifier (GUID) of the project (required).
        :return: dict - The API response containing the tokens associated with the project, in JSON format.
        """
        endpoint = GET_PROJECT_TOKENS_V1.format(id=project_id)
        response = self.api_service.get(endpoint=endpoint)
        validate_status_code(response)
        return parse_json_response(response, "get tokens for project with ID", project_id=project_id)

    def export_request_data(
            self,
            assistant_name: str = None,
            status: str = None,
            skip: int = 0,
            count: int = 0
    ) -> dict:
        """
        Exports request data based on the specified filters such as assistant name, status, and pagination parameters.

        :param assistant_name: str - The name of the assistant to filter the request data by (optional).
        :param status: str - The status to filter the request data by (optional).
        :param skip: int - The number of entries to skip in the response (default is 0).
        :param count: int - The number of entries to retrieve in the response (default is 0).
        :return: dict - The API response containing the requested data, in JSON format.
        """
        response = self.api_service.get(
            endpoint=GET_REQUEST_DATA_V1,
            params={
                "assistantName": assistant_name,
                "status": status,
                "skip": skip,
                "count": count
            }
        )
        validate_status_code(response)
        return parse_json_response(response, "export request data")

    def get_memberships(
            self,
            email: str = None,
            start_page: int = 1,
            page_size: int = 20,
            order_key: str = None,
            order_direction: str = "desc",
            role_types: str = None
    ) -> dict:
        """
        Retrieves a list of Organizations and Projects a user belongs to with their Roles.

        :param email: str - The email address of the user to search for (optional, case-insensitive).
        :param start_page: int - The page number for pagination (default is 1).
        :param page_size: int - The number of items per page (default is 20).
        :param order_key: str - Field for sorting. Only 'organizationName' is supported (optional).
        :param order_direction: str - Sort direction: 'asc' or 'desc' (default is 'desc').
        :param role_types: str - Comma-separated list of role types: 'backend', 'frontend' (optional, case-insensitive).
        :return: dict - The API response containing the list of organizations and projects with roles, in JSON format.
        """
        params = {
            "startPage": start_page,
            "pageSize": page_size,
            "orderDirection": order_direction
        }
        if email:
            params["email"] = email
        if order_key:
            params["orderKey"] = order_key
        if role_types:
            params["roleTypes"] = role_types

        response = self.api_service.get(endpoint=GET_MEMBERSHIPS_V2, params=params)
        validate_status_code(response)
        return parse_json_response(response, "get memberships")

    def get_project_memberships(
            self,
            email: str = None,
            start_page: int = 1,
            page_size: int = 20,
            order_key: str = None,
            order_direction: str = "desc",
            role_types: str = None
    ) -> dict:
        """
        Retrieves a list of Projects and Roles for a user within a specific Organization.

        :param email: str - The email address of the user to search for (optional, case-insensitive).
        :param start_page: int - The page number for pagination (default is 1).
        :param page_size: int - The number of items per page (default is 20).
        :param order_key: str - Field for sorting. Only 'projectName' is supported (optional).
        :param order_direction: str - Sort direction: 'asc' or 'desc' (default is 'desc').
        :param role_types: str - Comma-separated list of role types: 'backend', 'frontend' (optional, case-insensitive).
        :return: dict - The API response containing the list of projects with roles, in JSON format.
        """
        params = {
            "startPage": start_page,
            "pageSize": page_size,
            "orderDirection": order_direction
        }
        if email:
            params["email"] = email
        if order_key:
            params["orderKey"] = order_key
        if role_types:
            params["roleTypes"] = role_types

        response = self.api_service.get(endpoint=GET_PROJECT_MEMBERSHIPS_V2, params=params)
        validate_status_code(response)
        return parse_json_response(response, "get project memberships")

    def get_project_roles(
            self,
            project_id: str
    ) -> dict:
        """
        Retrieves all Roles supported by a specific Project.

        :param project_id: str - The unique identifier (GUID) of the project (required).
        :return: dict - The API response containing the list of roles for the project, in JSON format.
        """
        response = self.api_service.get(endpoint=GET_PROJECT_ROLES_V2, params={"projectId": project_id})
        validate_status_code(response)
        return parse_json_response(response, "get project roles for project", project_id=project_id)

    def get_project_members(
            self,
            project_id: str
    ) -> dict:
        """
        Retrieves all members and their Roles for a specific Project.

        :param project_id: str - The unique identifier (GUID) of the project (required).
        :return: dict - The API response containing the list of members with their roles, in JSON format.
        """
        response = self.api_service.get(endpoint=GET_PROJECT_MEMBERS_V2, params={"projectId": project_id})
        validate_status_code(response)
        return parse_json_response(response, "get project members for project", project_id=project_id)

    def get_organization_members(
            self,
            organization_id: str
    ) -> dict:
        """
        Retrieves all members and their Roles for a specific Organization.

        :param organization_id: str - The unique identifier (GUID) of the organization (required).
        :return: dict - The API response containing the list of members with their roles, in JSON format.
        """
        response = self.api_service.get(endpoint=GET_ORGANIZATION_MEMBERS_V2, params={"organizationId": organization_id})
        validate_status_code(response)
        return parse_json_response(response, "get organization members for organization", organization_id=organization_id)
