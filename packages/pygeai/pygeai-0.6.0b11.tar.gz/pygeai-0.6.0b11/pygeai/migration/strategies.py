import sys
from abc import ABC, abstractmethod
from typing import Optional

from pygeai import logger
from pygeai.core.models import Project, UsageLimit
from pygeai.core.base.responses import ErrorListResponse
from pygeai.core.utils.console import Console
from pygeai.core.files.managers import FileManager
from pygeai.core.files.models import File
from pygeai.lab.managers import AILabManager
from pygeai.lab.models import Agent, Tool, AgenticProcess, Task
from pygeai.organization.limits.managers import UsageLimitManager
from pygeai.organization.managers import OrganizationManager
from pygeai.assistant.managers import AssistantManager
from pygeai.assistant.rag.models import RAGAssistant


class MigrationStrategy(ABC):

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        self.from_api_key = from_api_key
        self.from_instance = from_instance
        self.to_api_key = to_api_key if to_api_key else from_api_key
        self.to_instance = to_instance if to_instance else from_instance

    @abstractmethod
    def migrate(self):
        pass

    def get_display_info(self) -> str:
        """
        Return a human-readable description of what this strategy will migrate.
        Used for progress tracking and logging.
        
        :return: String description like "agent abc-123" or "project MyProject"
        """
        return self.__class__.__name__.replace("MigrationStrategy", "").lower()


class ProjectMigrationStrategy(MigrationStrategy):
    """
    Migrate a project from a GEAI instance.
    The target project can be in another organization or the same one; in the same instance or another.
    
    Note: This strategy requires organization scope API keys for both source and destination,
    as it needs to create projects and manage usage limits using the Organization API.
    See: https://docs.globant.ai/en/wiki?22,Organization+API
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            from_project_id: str,
            to_project_name: str,
            admin_email: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.from_project_id = from_project_id
        self.to_project_name = to_project_name
        self.admin_email = admin_email
        self._source_manager = OrganizationManager(
            api_key=self.from_api_key,
            base_url=self.from_instance
        )
        self._destination_manager = OrganizationManager(
            api_key=self.to_api_key,
            base_url=self.to_instance
        )

    def get_display_info(self) -> str:
        return f"project '{self.to_project_name}'"

    def migrate(self):
        """
        Execute the project migration from source to destination instance.
        
        :return: The ID of the created project
        :raises ValueError: If project data cannot be retrieved or migration fails
        """
        new_project = self._migrate_project()
        project_name = getattr(new_project, 'name', 'Unknown')
        project_id = getattr(new_project, 'id', None)
        logger.info(f"Successfully migrated project {self.from_project_id} to {project_name}")
        return project_id

    def _migrate_project(self) -> Project:
        """
        Migrate the project data and create it in the destination instance.
        
        :return: The newly created project
        :raises ValueError: If project retrieval or creation fails
        """
        project_data = self._source_manager.get_project_data(project_id=self.from_project_id)

        if not hasattr(project_data, "project"):
            raise ValueError(f"Unable to retrieve project data for project {self.from_project_id}")

        new_project = project_data.project
        new_project.name = self.to_project_name
        new_project.email = self.admin_email
        
        logger.debug(f"Creating project with destination manager:")
        logger.debug(f"  - API Key (first 20 chars): {self.to_api_key[:20] if self.to_api_key else 'None'}...")
        logger.debug(f"  - Base URL: {self.to_instance}")
        logger.debug(f"  - Project Name: {self.to_project_name}")
        logger.debug(f"  - Admin Email: {self.admin_email}")
        
        try:
            response = self._destination_manager.create_project(new_project)
        except Exception as e:
            error_msg = f"Create project failed: {e}"
            logger.error(error_msg)
            logger.error(f"  - Operation: Create project")
            logger.error(f"  - Base URL: {self.to_instance}")
            logger.error(f"  - API Key used (first 20 chars): {self.to_api_key[:20] if self.to_api_key else 'None'}...")
            Console.write_stderr(f"\nDEBUG: Operation failed: Create project")
            Console.write_stderr(f"DEBUG: Base URL: {self.to_instance}")
            Console.write_stderr(f"DEBUG: API Key used (first 20 chars): {self.to_api_key[:20] if self.to_api_key else 'None'}...")
            raise ValueError(error_msg) from e

        if isinstance(response, ErrorListResponse):
            error_detail = response.to_dict()
            logger.error(f"Create project returned error response: {error_detail}")
            logger.error(f"  - Operation: Create project")
            logger.error(f"  - Base URL: {self.to_instance}")
            logger.error(f"  - API Key used (first 20 chars): {self.to_api_key[:20] if self.to_api_key else 'None'}...")
            Console.write_stderr(f"\nDEBUG: Operation failed: Create project")
            Console.write_stderr(f"DEBUG: Base URL: {self.to_instance}")
            Console.write_stderr(f"DEBUG: API Key used (first 20 chars): {self.to_api_key[:20] if self.to_api_key else 'None'}...")
            raise ValueError(f"Failed to create project: {error_detail}")

        if not response or not hasattr(response, "project"):
            raise ValueError("Project creation returned invalid response")

        return response.project

    def _migrate_assistants(self, new_project: Project):
        """
        Migrate assistants associated with the project.
        
        :param new_project: The newly created project to migrate assistants to
        """
        pass


class _LabResourceMigrationStrategy(MigrationStrategy):
    """
    Base class for migrating AI Lab resources (agents, tools, processes, tasks).
    Provides common functionality for resource migration.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self._source_manager = AILabManager(
            api_key=self.from_api_key,
            base_url=self.from_instance
        )
        self._destination_manager = AILabManager(
            api_key=self.to_api_key,
            base_url=self.to_instance
        )

    @abstractmethod
    def _get_resource(self, resource_id: str):
        """Retrieve the resource from source instance"""
        pass

    @abstractmethod
    def _create_resource(self, resource):
        """Create the resource in destination instance"""
        pass

    @abstractmethod
    def _get_resource_name(self) -> str:
        """Return the name of the resource type for logging/errors"""
        pass

    def get_display_info(self) -> str:
        resource_id = getattr(self, f"{self._get_resource_name()}_id", "unknown")
        return f"{self._get_resource_name()} {resource_id}"

    def migrate(self):
        """
        Execute the resource migration from source to destination instance.
        
        :raises ValueError: If resource retrieval or creation fails
        """
        resource_id = getattr(self, f"{self._get_resource_name()}_id")
        new_resource = self._migrate_resource(resource_id)
        Console.write_stdout(f"New {self._get_resource_name()} detail: \n{new_resource}")
        logger.info(f"Successfully migrated {self._get_resource_name()} {resource_id}")

    def _migrate_resource(self, resource_id: str):
        """
        Retrieve resource from source and create in destination.
        
        :param resource_id: The ID of the resource to migrate
        :return: The newly created resource
        :raises ValueError: If migration fails
        """
        try:
            source_resource = self._get_resource(resource_id)
            new_resource = self._create_resource(source_resource)
            return new_resource
        except Exception as e:
            logger.error(f"{self._get_resource_name().capitalize()} migration failed: {e}")
            raise ValueError(f"{self._get_resource_name().capitalize()} migration failed: {e}") from e


class AgentMigrationStrategy(_LabResourceMigrationStrategy):
    """
    Migrate an agent from a GEAI instance.
    The target project can be in another organization or the same one; in the same instance or another.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            agent_id: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.agent_id = agent_id

    def _get_resource(self, resource_id: str) -> Agent:
        agent = self._source_manager.get_agent(agent_id=resource_id)
        if not isinstance(agent, Agent):
            raise ValueError(f"Unable to retrieve agent {resource_id}")
        return agent

    def _create_resource(self, resource: Agent) -> Agent:
        return self._destination_manager.create_agent(agent=resource)

    def _get_resource_name(self) -> str:
        return "agent"


class ToolMigrationStrategy(_LabResourceMigrationStrategy):
    """
    Migrate a tool from a GEAI instance.
    The target project can be in another organization or the same one; in the same instance or another.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            tool_id: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.tool_id = tool_id

    def _get_resource(self, resource_id: str) -> Tool:
        tool = self._source_manager.get_tool(tool_id=resource_id)
        if not isinstance(tool, Tool):
            raise ValueError(f"Unable to retrieve tool {resource_id}")
        return tool

    def _create_resource(self, resource: Tool) -> Tool:
        return self._destination_manager.create_tool(tool=resource)

    def _get_resource_name(self) -> str:
        return "tool"


class AgenticProcessMigrationStrategy(_LabResourceMigrationStrategy):
    """
    Migrate an agentic process from a GEAI instance.
    The target project can be in another organization or the same one; in the same instance or another.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            process_id: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.process_id = process_id

    def _get_resource(self, resource_id: str) -> AgenticProcess:
        process = self._source_manager.get_process(process_id=resource_id)
        if not isinstance(process, AgenticProcess):
            raise ValueError(f"Unable to retrieve process {resource_id}")
        return process

    def _create_resource(self, resource: AgenticProcess) -> AgenticProcess:
        return self._destination_manager.create_process(process=resource)

    def _get_resource_name(self) -> str:
        return "process"


class TaskMigrationStrategy(_LabResourceMigrationStrategy):
    """
    Migrate a task from a GEAI instance.
    The target project can be in another organization or the same one; in the same instance or another.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            task_id: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.task_id = task_id

    def _get_resource(self, resource_id: str) -> Task:
        task = self._source_manager.get_task(task_id=resource_id)
        if not isinstance(task, Task):
            raise ValueError(f"Unable to retrieve task {resource_id}")
        return task

    def _create_resource(self, resource: Task) -> Task:
        return self._destination_manager.create_task(task=resource)

    def _get_resource_name(self) -> str:
        return "task"


class UsageLimitMigrationStrategy(MigrationStrategy):
    """
    Migrate usage limit from a GEAI organization.
    The target organization can be in the same instance or another.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            from_organization_id: str,
            to_organization_id: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.from_organization_id = from_organization_id
        self.to_organization_id = to_organization_id
        self._source_manager = UsageLimitManager(
            api_key=self.from_api_key,
            base_url=self.from_instance,
            organization_id=self.from_organization_id
        )
        self._destination_manager = UsageLimitManager(
            api_key=self.to_api_key,
            base_url=self.to_instance,
            organization_id=self.to_organization_id
        )

    def get_display_info(self) -> str:
        return f"usage limits (org {self.from_organization_id})"

    def migrate(self):
        """
        Execute the usage limit migration from source to destination organization.
        
        :raises ValueError: If usage limit retrieval or creation fails
        """
        new_limit = self._migrate_usage_limit()
        logger.info(f"Successfully migrated usage limit from org {self.from_organization_id} to {self.to_organization_id}")

    def _migrate_usage_limit(self) -> UsageLimit:
        """
        Retrieve latest usage limit from source and create in destination.
        
        :return: The newly created usage limit
        :raises ValueError: If migration fails
        """
        try:
            source_limit = self._source_manager.get_latest_usage_limit_from_organization()
            if not isinstance(source_limit, UsageLimit):
                raise ValueError("Unable to retrieve usage limit from source organization")

            source_limit.id = None
            new_limit = self._destination_manager.set_organization_usage_limit(source_limit)
            return new_limit
        except Exception as e:
            logger.error(f"Usage limit migration failed: {e}")
            raise ValueError(f"Usage limit migration failed: {e}") from e


class RAGAssistantMigrationStrategy(MigrationStrategy):
    """
    Migrate RAG assistant from a GEAI instance.
    The target instance can be the same or another.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            assistant_name: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.assistant_name = assistant_name
        self._source_manager = AssistantManager(
            api_key=self.from_api_key,
            base_url=self.from_instance
        )
        self._destination_manager = AssistantManager(
            api_key=self.to_api_key,
            base_url=self.to_instance
        )

    def get_display_info(self) -> str:
        return f"RAG assistant '{self.assistant_name}'"

    def migrate(self):
        """
        Execute the RAG assistant migration from source to destination instance.
        
        :raises ValueError: If assistant retrieval or creation fails
        """
        new_assistant = self._migrate_assistant()
        logger.info(f"Successfully migrated RAG assistant {self.assistant_name}")

    def _migrate_assistant(self) -> RAGAssistant:
        """
        Retrieve RAG assistant from source and create in destination.
        
        :return: The newly created RAG assistant
        :raises ValueError: If migration fails
        """
        try:
            source_assistant = self._source_manager.get_assistant_data(assistant_name=self.assistant_name)
            if not isinstance(source_assistant, RAGAssistant):
                raise ValueError(f"Assistant {self.assistant_name} is not a RAG assistant")

            source_assistant.id = None
            new_assistant = self._destination_manager.create_assistant(source_assistant)
            return new_assistant
        except Exception as e:
            logger.error(f"RAG assistant migration failed: {e}")
            raise ValueError(f"RAG assistant migration failed: {e}") from e


class FileMigrationStrategy(MigrationStrategy):
    """
    Migrate file from a GEAI project.
    The target project can be in another organization or the same one; in the same instance or another.
    """

    def __init__(
            self,
            from_api_key: str,
            from_instance: str,
            from_organization_id: str,
            from_project_id: str,
            to_organization_id: str,
            to_project_id: str,
            file_id: str,
            to_api_key: Optional[str] = None,
            to_instance: Optional[str] = None
    ):
        super().__init__(from_api_key, from_instance, to_api_key, to_instance)
        self.from_organization_id = from_organization_id
        self.from_project_id = from_project_id
        self.to_organization_id = to_organization_id
        self.to_project_id = to_project_id
        self.file_id = file_id
        self._source_manager = FileManager(
            api_key=self.from_api_key,
            base_url=self.from_instance,
            organization_id=self.from_organization_id,
            project_id=self.from_project_id
        )
        self._destination_manager = FileManager(
            api_key=self.to_api_key,
            base_url=self.to_instance,
            organization_id=self.to_organization_id,
            project_id=self.to_project_id
        )

    def get_display_info(self) -> str:
        return f"file {self.file_id}"

    def migrate(self):
        """
        Execute the file migration from source to destination project.
        
        :raises ValueError: If file retrieval or upload fails
        """
        new_file = self._migrate_file()
        logger.info(f"Successfully migrated file {self.file_id}")

    def _migrate_file(self) -> File:
        """
        Retrieve file from source and upload to destination.
        
        :return: The newly uploaded file
        :raises ValueError: If migration fails
        """
        try:
            source_file = self._source_manager.get_file_data(file_id=self.file_id)
            if not isinstance(source_file, File):
                raise ValueError(f"Unable to retrieve file {self.file_id}")

            file_content = self._source_manager.get_file_content(file_id=self.file_id)
            upload_response = self._destination_manager.upload_file_from_content(
                file_name=source_file.name,
                content=file_content,
                folder=None
            )
            return upload_response.file
        except Exception as e:
            logger.error(f"File migration failed: {e}")
            raise ValueError(f"File migration failed: {e}") from e
