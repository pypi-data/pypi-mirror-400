from pygeai import logger
from pygeai.core.base.mappers import ErrorMapper, ResponseMapper
from pygeai.core.handlers import ErrorHandler
from pygeai.core.models import Project
from pygeai.core.base.responses import EmptyResponse
from pygeai.organization.clients import OrganizationClient
from pygeai.organization.mappers import OrganizationResponseMapper
from pygeai.organization.responses import AssistantListResponse, ProjectListResponse, ProjectDataResponse, \
    ProjectTokensResponse, ProjectItemListResponse, MembershipsResponse, ProjectMembershipsResponse, \
    ProjectRolesResponse, ProjectMembersResponse, OrganizationMembersResponse
from pygeai.core.common.exceptions import APIError


class OrganizationManager:
    """
    Manager that operates as an abstraction level over the clients, designed to handle calls receiving and
    returning objects when appropriate.
    If errors are found in the response, they are processed to raise an APIError.
    """

    def __init__(self, api_key: str = None, base_url: str = None, alias: str = "default"):
        self.__organization_client = OrganizationClient(api_key=api_key, base_url=base_url, alias=alias)

    def get_assistant_list(
            self,
            detail: str = "summary"
    ) -> AssistantListResponse:
        """
        Retrieves a list of assistants with the specified level of detail.

        This method calls `OrganizationClient.get_assistant_list` to fetch assistant data
        and maps the response using `OrganizationResponseMapper` into an `AssistantListResponse` object.

        :param detail: str - The level of detail to include in the response. Possible values:
            - "summary": Provides a summarized list of assistants. (Default)
            - "full": Provides a detailed list of assistants. (Optional)
        :return: AssistantListResponse - The mapped response containing the list of assistants.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_assistant_list(detail=detail)
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving assistant list: {error}")
            raise APIError(f"Error received while retrieving assistant list: {error}")

        result = OrganizationResponseMapper.map_to_assistant_list_response(response_data)
        # TODO -> Add assistant list from plugins API
        return result

    def get_project_list(
            self,
            detail: str = "summary",
            name: str = None
    ) -> ProjectListResponse:
        """
        Retrieves a list of projects with the specified level of detail and optional filtering by name.

        This method calls `OrganizationClient.get_project_list` to fetch project data
        and maps the response using `OrganizationResponseMapper` into a `ProjectListResponse` object.

        :param detail: str - The level of detail to include in the response. Possible values:
            - "summary": Provides a summarized list of projects. (Default)
            - "full": Provides a detailed list of projects. (Optional)
        :param name: str, optional - Filters projects by name. If not provided, all projects are returned.
        :return: ProjectListResponse - The mapped response containing the list of projects.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_project_list(
            detail=detail,
            name=name
            )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving project list: {error}")
            raise APIError(f"Error received while retrieving project list: {error}")

        result = OrganizationResponseMapper.map_to_project_list_response(response_data)
        return result

    def get_project_data(
            self,
            project_id: str
    ) -> ProjectDataResponse:
        """
        Retrieves detailed data for a specific project.

        This method calls `OrganizationClient.get_project_data` to fetch project details
        and maps the response using `OrganizationResponseMapper` into a `ProjectDataResponse` object.

        :param project_id: str - The unique identifier of the project to retrieve.
        :return: ProjectDataResponse - The mapped response containing project details.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_project_data(
            project_id=project_id
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving project data: {error}")
            raise APIError(f"Error received while retrieving project data: {error}")

        result = OrganizationResponseMapper.map_to_project_data(response_data)
        return result

    def create_project(
            self,
            project: Project
    ) -> ProjectDataResponse:
        """
        Creates a new project with the given details and optional usage limit settings.

        This method calls `OrganizationClient.create_project` to create a new project and maps the response
        using `OrganizationResponseMapper` into a `ProjectDataResponse` object.

        :param project: Project - The project object containing details such as name, email, and description.
        :return: ProjectDataResponse - The mapped response containing the created project details.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.create_project(
            name=project.name,
            email=project.email,
            description=project.description,
            usage_limit={
                "subscriptionType": project.usage_limit.subscription_type,
                "usageUnit": project.usage_limit.usage_unit,
                "softLimit": project.usage_limit.soft_limit,
                "hardLimit": project.usage_limit.hard_limit,
                "renewalStatus": project.usage_limit.renewal_status,
            } if project.usage_limit is not None else None,
        )

        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while creating project: {error}")
            raise APIError(f"Error received while creating project: {error}")

        result = OrganizationResponseMapper.map_to_project_data(response_data)
        return result

    def update_project(
            self,
            project: Project
    ) -> ProjectDataResponse:
        """
        Updates an existing project with the provided details.

        This method calls `OrganizationClient.update_project` to update project information and maps the response
        using `OrganizationResponseMapper` into a `ProjectDataResponse` object.

        :param project: Project - The project object containing updated details such as project ID, name, and description.
        :return: ProjectDataResponse - The mapped response containing the updated project details.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.update_project(
            project_id=project.id,
            name=project.name,
            description=project.description
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while updating project: {error}")
            raise APIError(f"Error received while updating project: {error}")

        result = OrganizationResponseMapper.map_to_project_data(response_data)
        return result

    def delete_project(
            self,
            project_id: str
    ) -> EmptyResponse:
        """
        Deletes a project by its unique identifier.

        This method calls `OrganizationClient.delete_project` to remove a project and maps the response
        using `ResponseMapper.map_to_empty_response`.

        :param project_id: str - The unique identifier of the project to be deleted.
        :return: EmptyResponse - An empty response indicating successful deletion.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.delete_project(
            project_id=project_id
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while deleting project: {error}")
            raise APIError(f"Error received while deleting project: {error}")

        result = ResponseMapper.map_to_empty_response(response_data or "Project deleted successfully")
        return result

    def get_project_tokens(
            self,
            project_id: str
    ) -> ProjectTokensResponse:
        """
        Retrieves a list of tokens associated with a specific project.

        This method calls `OrganizationClient.get_project_tokens` to fetch token data and maps the response
        using `OrganizationResponseMapper.map_to_token_list_response`.

        :param project_id: str - The unique identifier of the project whose tokens are to be retrieved.
        :return: ProjectTokensResponse - The mapped response containing the list of project tokens.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_project_tokens(
            project_id=project_id
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving project tokens: {error}")
            raise APIError(f"Error received while retrieving project tokens: {error}")

        result = OrganizationResponseMapper.map_to_token_list_response(response_data)
        return result

    def export_request_data(
            self,
            assistant_name: str = None,
            status: str = None,
            skip: int = 0,
            count: int = 0
    ) -> ProjectItemListResponse:
        """
        Exports request data based on specified filters.

        This method calls `OrganizationClient.export_request_data` to retrieve request data
        filtered by assistant name, status, and pagination parameters. The response is mapped
        using `OrganizationResponseMapper.map_to_item_list_response`.

        :param assistant_name: str, optional - Filters requests by assistant name. If not provided, all assistants are included.
        :param status: str, optional - Filters requests by status. If not provided, all statuses are included.
        :param skip: int, optional - The number of records to skip for pagination. Default is 0.
        :param count: int, optional - The number of records to retrieve. Default is 0 (no limit).
        :return: ProjectItemListResponse - The mapped response containing the exported request data.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.export_request_data(
            assistant_name=assistant_name,
            status=status,
            skip=skip,
            count=count
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while exporting request data: {error}")
            raise APIError(f"Error received while exporting request data: {error}")

        result = OrganizationResponseMapper.map_to_item_list_response(response_data)
        return result

    def get_memberships(
            self,
            email: str = None,
            start_page: int = 1,
            page_size: int = 20,
            order_key: str = None,
            order_direction: str = "desc",
            role_types: str = None
    ) -> MembershipsResponse:
        """
        Retrieves a list of Organizations and Projects a user belongs to with their Roles.

        This method calls `OrganizationClient.get_memberships` to fetch membership data
        and maps the response using `OrganizationResponseMapper.map_to_memberships_response`.

        :param email: str, optional - The email address of the user to search for (case-insensitive).
        :param start_page: int - The page number for pagination (default is 1).
        :param page_size: int - The number of items per page (default is 20).
        :param order_key: str, optional - Field for sorting. Only 'organizationName' is supported.
        :param order_direction: str - Sort direction: 'asc' or 'desc' (default is 'desc').
        :param role_types: str, optional - Comma-separated list of role types: 'backend', 'frontend' (case-insensitive).
        :return: MembershipsResponse - The mapped response containing organizations and projects with roles.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_memberships(
            email=email,
            start_page=start_page,
            page_size=page_size,
            order_key=order_key,
            order_direction=order_direction,
            role_types=role_types
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving memberships: {error}")
            raise APIError(f"Error received while retrieving memberships: {error}")

        result = OrganizationResponseMapper.map_to_memberships_response(response_data)
        return result

    def get_project_memberships(
            self,
            email: str = None,
            start_page: int = 1,
            page_size: int = 20,
            order_key: str = None,
            order_direction: str = "desc",
            role_types: str = None
    ) -> ProjectMembershipsResponse:
        """
        Retrieves a list of Projects and Roles for a user within a specific Organization.

        This method calls `OrganizationClient.get_project_memberships` to fetch project membership data
        and maps the response using `OrganizationResponseMapper.map_to_project_memberships_response`.

        :param email: str, optional - The email address of the user to search for (case-insensitive).
        :param start_page: int - The page number for pagination (default is 1).
        :param page_size: int - The number of items per page (default is 20).
        :param order_key: str, optional - Field for sorting. Only 'projectName' is supported.
        :param order_direction: str - Sort direction: 'asc' or 'desc' (default is 'desc').
        :param role_types: str, optional - Comma-separated list of role types: 'backend', 'frontend' (case-insensitive).
        :return: ProjectMembershipsResponse - The mapped response containing projects with roles.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_project_memberships(
            email=email,
            start_page=start_page,
            page_size=page_size,
            order_key=order_key,
            order_direction=order_direction,
            role_types=role_types
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving project memberships: {error}")
            raise APIError(f"Error received while retrieving project memberships: {error}")

        result = OrganizationResponseMapper.map_to_project_memberships_response(response_data)
        return result

    def get_project_roles(
            self,
            project_id: str
    ) -> ProjectRolesResponse:
        """
        Retrieves all Roles supported by a specific Project.

        This method calls `OrganizationClient.get_project_roles` to fetch project roles
        and maps the response using `OrganizationResponseMapper.map_to_project_roles_response`.

        :param project_id: str - The unique identifier of the project.
        :return: ProjectRolesResponse - The mapped response containing the list of roles.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_project_roles(
            project_id=project_id
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving project roles: {error}")
            raise APIError(f"Error received while retrieving project roles: {error}")

        result = OrganizationResponseMapper.map_to_project_roles_response(response_data)
        return result

    def get_project_members(
            self,
            project_id: str
    ) -> ProjectMembersResponse:
        """
        Retrieves all members and their Roles for a specific Project.

        This method calls `OrganizationClient.get_project_members` to fetch project members
        and maps the response using `OrganizationResponseMapper.map_to_project_members_response`.

        :param project_id: str - The unique identifier of the project.
        :return: ProjectMembersResponse - The mapped response containing members with their roles.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_project_members(
            project_id=project_id
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving project members: {error}")
            raise APIError(f"Error received while retrieving project members: {error}")

        result = OrganizationResponseMapper.map_to_project_members_response(response_data)
        return result

    def get_organization_members(
            self,
            organization_id: str
    ) -> OrganizationMembersResponse:
        """
        Retrieves all members and their Roles for a specific Organization.

        This method calls `OrganizationClient.get_organization_members` to fetch organization members
        and maps the response using `OrganizationResponseMapper.map_to_organization_members_response`.

        :param organization_id: str - The unique identifier of the organization.
        :return: OrganizationMembersResponse - The mapped response containing members with their roles.
        :raises APIError: If the API returns errors.
        """
        response_data = self.__organization_client.get_organization_members(
            organization_id=organization_id
        )
        if ErrorHandler.has_errors(response_data):
            error = ErrorHandler.extract_error(response_data)
            logger.error(f"Error received while retrieving organization members: {error}")
            raise APIError(f"Error received while retrieving organization members: {error}")

        result = OrganizationResponseMapper.map_to_organization_members_response(response_data)
        return result
