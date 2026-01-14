from typing import Tuple, Dict, Any, Optional, List
from pygeai import logger
from pygeai.cli.commands import Command, Option, ArgumentsEnum
from pygeai.cli.commands.builders import build_help_text
from pygeai.cli.texts.help import MIGRATE_HELP_TEXT
from pygeai.core.common.exceptions import MissingRequirementException
from pygeai.core.utils.console import Console
from pygeai.lab.managers import AILabManager
from pygeai.lab.models import FilterSettings
from pygeai.assistant.managers import AssistantManager
from pygeai.assistant.rag.clients import RAGAssistantClient
from pygeai.assistant.rag.mappers import RAGAssistantMapper
from pygeai.core.files.managers import FileManager
from pygeai.migration.strategies import (
    ProjectMigrationStrategy,
    AgentMigrationStrategy,
    ToolMigrationStrategy,
    AgenticProcessMigrationStrategy,
    TaskMigrationStrategy,
    UsageLimitMigrationStrategy,
    RAGAssistantMigrationStrategy,
    FileMigrationStrategy
)
from pygeai.migration.tools import MigrationTool, MigrationPlan, MigrationOrchestrator
from pygeai.admin.clients import AdminClient


def show_help() -> None:
    """
    Displays help text in stdout.
    """
    help_text = build_help_text(migrate_commands, MIGRATE_HELP_TEXT)
    Console.write_stdout(help_text)


def prompt_with_retry(
    prompt_message: str,
    valid_choices: Optional[list] = None,
    allow_empty: bool = False
) -> str:
    """
    Prompt user for input with validation and retry logic.
    
    :param prompt_message: Message to display when prompting
    :param valid_choices: Optional list of valid input choices
    :param allow_empty: Whether to allow empty input
    :return: User's validated input string
    """
    while True:
        user_input = input(prompt_message).strip()
        
        if not user_input and not allow_empty:
            Console.write_stdout("Error: Input cannot be empty. Please try again.")
            continue
        
        if valid_choices and user_input not in valid_choices:
            Console.write_stdout(f"Error: Invalid choice '{user_input}'. Valid options: {', '.join(valid_choices)}")
            continue
        
        return user_input


def prompt_resource_selection(
    resource_type: str,
    items: list,
    id_field: str = "id",
    name_field: str = "name"
) -> Optional[str]:
    """
    Display a list of resources and let the user select which ones to migrate.
    
    :param resource_type: Type of resource being selected (for display purposes)
    :param items: List of resource items to display
    :param id_field: Name of the attribute containing the resource ID
    :param name_field: Name of the attribute containing the resource name
    :return: Comma-separated string of selected IDs, 'all' for all resources, or None to cancel
    """
    if not items:
        Console.write_stdout(f"No {resource_type} found.")
        return None
    
    Console.write_stdout(f"\nAvailable {resource_type}:")
    Console.write_stdout("  0. Cancel (don't migrate this resource type)")
    
    for idx, item in enumerate(items, 1):
        item_id = getattr(item, id_field, None)
        item_name = getattr(item, name_field, None) if hasattr(item, name_field) else None
        if item_name:
            Console.write_stdout(f"  {idx}. {item_name} (ID: {item_id})")
        else:
            Console.write_stdout(f"  {idx}. {item_id}")
    
    while True:
        selection = input(f"\nSelect {resource_type} (comma-separated numbers, or empty for all): ").strip()
        
        if not selection:
            return "all"
        
        if selection == "0":
            return None
        
        try:
            indices = [int(x.strip()) for x in selection.split(",")]
            if any(i < 0 or i > len(items) for i in indices):
                Console.write_stdout(f"Error: Invalid selection. Numbers must be between 0 and {len(items)}.")
                continue
            
            if 0 in indices:
                return None
            
            selected_ids = [getattr(items[i-1], id_field) for i in indices]
            return ",".join(str(sid) for sid in selected_ids)
        except (ValueError, IndexError) as e:
            Console.write_stdout(f"Error: Invalid input format. Please enter comma-separated numbers.")
            continue


def get_source_configuration() -> Tuple[str, str, str, Optional[str]]:
    """
    Prompt user for source configuration and retrieve organization ID.
    
    :return: Tuple of (api_key, instance_url, project_id, organization_id)
    """
    Console.write_stdout("\n--- Source Configuration ---")
    from_api_key = prompt_with_retry("Source API key: ")
    from_instance = prompt_with_retry("Source instance URL: ")
    from_project_id = prompt_with_retry("Source project ID: ")
    
    admin_client = AdminClient(api_key=from_api_key, base_url=from_instance)
    source_token_info = admin_client.validate_api_token()
    from_organization_id = source_token_info.get("organizationId")
    
    return from_api_key, from_instance, from_project_id, from_organization_id


def get_destination_configuration(
    same_instance: bool,
    from_instance: str,
    from_api_key: str,
    from_organization_id: Optional[str],
    creating_project: bool
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Configure destination instance settings based on migration type.
    
    :param same_instance: Whether migration is within the same instance
    :param from_instance: Source instance URL
    :param from_api_key: Source API key
    :param from_organization_id: Source organization ID
    :param creating_project: Whether a new project will be created
    :return: Tuple of (instance_url, api_key, organization_id)
    """
    if same_instance:
        to_instance = from_instance
        to_organization_id = from_organization_id
        Console.write_stdout(f"Destination instance: {to_instance} (same as source)")
        Console.write_stdout(f"Destination organization ID: {to_organization_id} (same as source)")
        
        if creating_project:
            to_api_key = None
            Console.write_stdout("Destination API key: (will be created after project creation)")
        else:
            to_api_key = prompt_with_retry("Destination API key: ")
    else:
        Console.write_stdout("\n--- Destination Configuration ---")
        to_instance = prompt_with_retry("Destination instance URL: ")
        
        if creating_project:
            to_api_key = None
            to_organization_id = None
            Console.write_stdout("Destination API key: (will be created after project creation)")
            Console.write_stdout("Destination organization ID: (will be retrieved after project creation)")
        else:
            to_api_key = prompt_with_retry("Destination API key: ")
            dest_admin_client = AdminClient(api_key=to_api_key, base_url=to_instance)
            dest_token_info = dest_admin_client.validate_api_token()
            to_organization_id = dest_token_info.get("organizationId")
    
    return to_instance, to_api_key, to_organization_id


def get_project_creation_info(same_instance: bool) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Prompt user for project creation information.
    
    :param same_instance: Whether migration is within the same instance
    :return: Tuple of (from_org_api_key, to_org_api_key, project_name, admin_email, project_id)
    """
    create_project = prompt_with_retry(
        "Create new destination project? (y/n): ",
        valid_choices=["y", "n"]
    )
    
    from_organization_api_key = None
    to_organization_api_key = None
    to_project_name = None
    admin_email = None
    to_project_id = None
    
    if create_project == "y":
        from_organization_api_key = prompt_with_retry("Source organization API key: ")
        if same_instance:
            to_organization_api_key = from_organization_api_key
            Console.write_stdout("Destination organization API key: (same as source)")
        else:
            to_organization_api_key = prompt_with_retry("Destination organization API key: ")
        to_project_name = prompt_with_retry("New project name: ")
        admin_email = prompt_with_retry("Admin email: ")
    else:
        to_project_id = prompt_with_retry("Destination project ID: ")
    
    return from_organization_api_key, to_organization_api_key, to_project_name, admin_email, to_project_id


def select_resource_types() -> List[int]:
    """
    Prompt user to select which resource types to migrate.
    
    :return: List of integers representing selected resource types (1-7)
    """
    Console.write_stdout("\n--- Resource Type Selection ---")
    Console.write_stdout("Which resource types do you want to migrate?")
    Console.write_stdout("  1. Agents")
    Console.write_stdout("  2. Tools")
    Console.write_stdout("  3. Agentic Processes")
    Console.write_stdout("  4. Tasks")
    Console.write_stdout("  5. RAG Assistants")
    Console.write_stdout("  6. Files")
    Console.write_stdout("  7. Usage Limits")
    
    while True:
        resource_choice = input("\nSelect resource types (comma-separated numbers, or empty for all): ").strip()
        if not resource_choice:
            return [1, 2, 3, 4, 5, 6, 7]
        try:
            resource_types = [int(x.strip()) for x in resource_choice.split(",")]
            if any(i < 1 or i > 7 for i in resource_types):
                Console.write_stdout("Error: Invalid selection. Numbers must be between 1 and 7.")
                continue
            return resource_types
        except ValueError:
            Console.write_stdout("Error: Invalid input format. Please enter comma-separated numbers.")
            continue


def fetch_and_select_agents(lab_manager: AILabManager) -> Optional[str]:
    """
    Fetch and prompt user to select agents for migration.
    
    :param lab_manager: AI Lab manager instance
    :return: Comma-separated IDs, 'all', or None
    """
    try:
        agent_list = lab_manager.get_agent_list(FilterSettings(count=1000))
        agents = [a for a in agent_list.agents if a.id]
        if agents:
            selection = prompt_resource_selection("agents", agents, id_field="id", name_field="name")
            return selection
    except Exception as e:
        Console.write_stdout(f"Warning: Could not retrieve agents: {e}")
    return None


def fetch_and_select_tools(lab_manager: AILabManager) -> Optional[str]:
    """
    Fetch and prompt user to select tools for migration.
    
    :param lab_manager: AI Lab manager instance
    :return: Comma-separated IDs, 'all', or None
    """
    try:
        tool_list = lab_manager.list_tools(FilterSettings(count=1000))
        tools = [t for t in tool_list.tools if t.id]
        if tools:
            selection = prompt_resource_selection("tools", tools, id_field="id", name_field="name")
            return selection
    except Exception as e:
        Console.write_stdout(f"Warning: Could not retrieve tools: {e}")
    return None


def fetch_and_select_processes(lab_manager: AILabManager) -> Optional[str]:
    """
    Fetch and prompt user to select processes for migration.
    
    :param lab_manager: AI Lab manager instance
    :return: Comma-separated IDs, 'all', or None
    """
    try:
        process_list = lab_manager.list_processes(FilterSettings(count=1000))
        processes = [p for p in process_list.processes if p.id]
        if processes:
            selection = prompt_resource_selection("agentic processes", processes, id_field="id", name_field="name")
            return selection
    except Exception as e:
        Console.write_stdout(f"Warning: Could not retrieve agentic processes: {e}")
    return None


def fetch_and_select_tasks(lab_manager: AILabManager) -> Optional[str]:
    """
    Fetch and prompt user to select tasks for migration.
    
    :param lab_manager: AI Lab manager instance
    :return: Comma-separated IDs, 'all', or None
    """
    try:
        task_list = lab_manager.list_tasks(FilterSettings(count=1000))
        tasks = [t for t in task_list.tasks if t.id]
        if tasks:
            selection = prompt_resource_selection("tasks", tasks, id_field="id", name_field="name")
            return selection
    except Exception as e:
        Console.write_stdout(f"Warning: Could not retrieve tasks: {e}")
    return None


def fetch_and_select_rag_assistants(from_api_key: str, from_instance: str) -> Optional[str]:
    """
    Fetch and prompt user to select RAG assistants for migration.
    
    :param from_api_key: Source API key
    :param from_instance: Source instance URL
    :return: Comma-separated names, 'all', or None
    """
    try:
        rag_client = RAGAssistantClient(api_key=from_api_key, base_url=from_instance)
        assistant_data = rag_client.get_assistants_from_project()
        assistants_raw = assistant_data.get("assistants", [])
        assistant_list = [RAGAssistantMapper.map_to_rag_assistant(a) for a in assistants_raw] if assistants_raw else []
        if assistant_list:
            selection = prompt_resource_selection("RAG assistants", assistant_list, id_field="name", name_field="name")
            return selection
    except Exception as e:
        Console.write_stdout(f"Warning: Could not retrieve RAG assistants: {e}")
    return None


def fetch_and_select_files(
    from_api_key: str,
    from_instance: str,
    from_organization_id: str,
    from_project_id: str
) -> Optional[str]:
    """
    Fetch and prompt user to select files for migration.
    
    :param from_api_key: Source API key
    :param from_instance: Source instance URL
    :param from_organization_id: Source organization ID
    :param from_project_id: Source project ID
    :return: Comma-separated file IDs, 'all', or None
    """
    try:
        file_manager = FileManager(
            api_key=from_api_key,
            base_url=from_instance,
            organization_id=from_organization_id,
            project_id=from_project_id
        )
        file_list_response = file_manager.get_file_list()
        files = [f for f in file_list_response.files if f.id]
        if files:
            selection = prompt_resource_selection("files", files, id_field="id", name_field="filename")
            return selection
    except Exception as e:
        Console.write_stdout(f"Warning: Could not retrieve files: {e}")
    return None


def handle_usage_limits_keys(
    same_instance: bool,
    from_organization_api_key: Optional[str],
    to_organization_api_key: Optional[str]
) -> Tuple[str, str]:
    """
    Ensure organization API keys are available for usage limits migration.
    
    :param same_instance: Whether migration is within the same instance
    :param from_organization_api_key: Source organization API key (may be None)
    :param to_organization_api_key: Destination organization API key (may be None)
    :return: Tuple of (from_org_api_key, to_org_api_key)
    """
    if not from_organization_api_key:
        from_organization_api_key = prompt_with_retry("Source organization API key (required for usage limits): ")
    if same_instance:
        to_organization_api_key = from_organization_api_key
    elif not to_organization_api_key:
        to_organization_api_key = prompt_with_retry("Destination organization API key (required for usage limits): ")
    
    return from_organization_api_key, to_organization_api_key


def show_summary_and_confirm(
    from_instance: str,
    from_project_id: str,
    to_instance: str,
    to_project_name: Optional[str],
    to_project_id: Optional[str],
    selected_resources: Dict[str, Any]
) -> Tuple[bool, bool]:
    """
    Display migration summary and prompt user for confirmation and error handling preference.
    
    :param from_instance: Source instance URL
    :param from_project_id: Source project ID
    :param to_instance: Destination instance URL
    :param to_project_name: Destination project name (if creating new project)
    :param to_project_id: Destination project ID (if using existing project)
    :param selected_resources: Dictionary of selected resources to migrate
    :return: Tuple of (confirmation, stop_on_error) - whether user confirmed migration and whether to stop on errors
    """
    Console.write_stdout("\n--- Migration Summary ---")
    Console.write_stdout(f"Source: {from_instance} / Project: {from_project_id}")
    Console.write_stdout(f"Destination: {to_instance} / Project: {to_project_name or to_project_id}")
    Console.write_stdout(f"Resources: {', '.join(selected_resources.keys()) if selected_resources else 'None'}")
    Console.write_stdout("")
    
    stop_on_error_response = prompt_with_retry("Stop migration on first error? (Y/n): ", valid_choices=["y", "n", "Y", "N", ""])
    stop_on_error = stop_on_error_response.lower() != "n"
    
    confirm = prompt_with_retry("Proceed with migration? (y/n): ", valid_choices=["y", "n"])
    return confirm == "y", stop_on_error


def build_option_list_and_execute(
    from_api_key: str,
    from_instance: str,
    from_project_id: str,
    from_organization_id: Optional[str],
    from_organization_api_key: Optional[str],
    to_api_key: Optional[str],
    to_instance: str,
    to_project_id: Optional[str],
    to_organization_id: Optional[str],
    to_organization_api_key: Optional[str],
    to_project_name: Optional[str],
    admin_email: Optional[str],
    selected_resources: Dict[str, Any],
    stop_on_error: bool
) -> None:
    """
    Build option list from interactive mode selections and execute migration.
    
    :param from_api_key: Source API key
    :param from_instance: Source instance URL
    :param from_project_id: Source project ID
    :param from_organization_id: Source organization ID
    :param from_organization_api_key: Source organization API key
    :param to_api_key: Destination API key
    :param to_instance: Destination instance URL
    :param to_project_id: Destination project ID
    :param to_organization_id: Destination organization ID
    :param to_organization_api_key: Destination organization API key
    :param to_project_name: New project name (if creating)
    :param admin_email: Admin email (if creating project)
    :param selected_resources: Dictionary of selected resources to migrate
    :param stop_on_error: Whether to stop migration on first error
    """
    option_list = []
    option_list.append((type('obj', (object,), {'name': 'from_api_key'})(), from_api_key))
    option_list.append((type('obj', (object,), {'name': 'from_instance'})(), from_instance))
    option_list.append((type('obj', (object,), {'name': 'from_project_id'})(), from_project_id))
    option_list.append((type('obj', (object,), {'name': 'from_organization_api_key'})(), from_organization_api_key))
    
    if from_organization_id:
        option_list.append((type('obj', (object,), {'name': 'from_organization_id'})(), from_organization_id))
    
    option_list.append((type('obj', (object,), {'name': 'to_api_key'})(), to_api_key))
    option_list.append((type('obj', (object,), {'name': 'to_instance'})(), to_instance))
    option_list.append((type('obj', (object,), {'name': 'to_organization_api_key'})(), to_organization_api_key))
    
    if to_project_id:
        option_list.append((type('obj', (object,), {'name': 'to_project_id'})(), to_project_id))
    if to_project_name:
        option_list.append((type('obj', (object,), {'name': 'to_project_name'})(), to_project_name))
    if admin_email:
        option_list.append((type('obj', (object,), {'name': 'admin_email'})(), admin_email))
    if to_organization_id:
        option_list.append((type('obj', (object,), {'name': 'to_organization_id'})(), to_organization_id))
    
    for resource_type, value in selected_resources.items():
        option_list.append((type('obj', (object,), {'name': resource_type})(), value))
    
    option_list.append((type('obj', (object,), {'name': 'stop_on_error'})(), "1" if stop_on_error else "0"))
    
    clone_project(option_list)


def clone_project_interactively() -> None:
    """
    Run interactive migration wizard with step-by-step prompts for all configuration.
    """
    Console.write_stdout("")
    Console.write_stdout("=" * 80)
    Console.write_stdout("PROJECT MIGRATION ASSISTANT")
    Console.write_stdout("=" * 80)
    Console.write_stdout("")
    
    migration_type = prompt_with_retry(
        "Migration type (1=same instance, 2=cross instance): ",
        valid_choices=["1", "2"]
    )
    same_instance = migration_type == "1"
    
    from_api_key, from_instance, from_project_id, from_organization_id = get_source_configuration()
    from_organization_api_key, to_organization_api_key, to_project_name, admin_email, to_project_id = get_project_creation_info(same_instance)
    
    creating_project = bool(to_project_name and admin_email)
    to_instance, to_api_key, to_organization_id = get_destination_configuration(
        same_instance, from_instance, from_api_key, from_organization_id, creating_project
    )
    
    resource_types_to_migrate = select_resource_types()
    
    Console.write_stdout("\n--- Retrieving Available Resources ---")
    lab_manager = AILabManager(api_key=from_api_key, base_url=from_instance)
    
    selected_resources = {}
    
    if 1 in resource_types_to_migrate:
        selection = fetch_and_select_agents(lab_manager)
        if selection:
            selected_resources["agents"] = selection
    
    if 2 in resource_types_to_migrate:
        selection = fetch_and_select_tools(lab_manager)
        if selection:
            selected_resources["tools"] = selection
    
    if 3 in resource_types_to_migrate:
        selection = fetch_and_select_processes(lab_manager)
        if selection:
            selected_resources["agentic_processes"] = selection
    
    if 4 in resource_types_to_migrate:
        selection = fetch_and_select_tasks(lab_manager)
        if selection:
            selected_resources["tasks"] = selection
    
    if 5 in resource_types_to_migrate:
        selection = fetch_and_select_rag_assistants(from_api_key, from_instance)
        if selection:
            selected_resources["rag_assistants"] = selection
    
    if 6 in resource_types_to_migrate:
        selection = fetch_and_select_files(from_api_key, from_instance, from_organization_id, from_project_id)
        if selection:
            selected_resources["files"] = selection
    
    if 7 in resource_types_to_migrate:
        from_organization_api_key, to_organization_api_key = handle_usage_limits_keys(
            same_instance, from_organization_api_key, to_organization_api_key
        )
        selected_resources["usage_limits"] = True
    
    confirmed, stop_on_error = show_summary_and_confirm(from_instance, from_project_id, to_instance, to_project_name, to_project_id, selected_resources)
    if not confirmed:
        Console.write_stdout("Migration cancelled.")
        return
    
    build_option_list_and_execute(
        from_api_key, from_instance, from_project_id, from_organization_id, from_organization_api_key,
        to_api_key, to_instance, to_project_id, to_organization_id, to_organization_api_key,
        to_project_name, admin_email, selected_resources, stop_on_error
    )


def clone_project(option_list: list) -> None:
    """
    Clone a project with selected components from source to destination instance.
    
    Supports migration of agents, tools, agentic processes, tasks, usage limits,
    RAG assistants, and files between GenExus AI instances.
    
    :param option_list: List of (option_flag, option_value) tuples from CLI parsing
    """
    interactive_mode = False
    for option_flag, option_arg in option_list:
        if option_flag.name == "interactive":
            interactive_mode = True
            break
    
    if interactive_mode:
        clone_project_interactively()
        return
    
    from_api_key = None
    from_organization_api_key = None
    from_instance = None
    from_project_id = None
    from_organization_id = None
    to_api_key = None
    to_organization_api_key = None
    to_instance = None
    to_project_id = None
    to_organization_id = None
    to_project_name = None
    admin_email = None
    
    migrate_all = False
    migrate_agents = False
    migrate_tools = False
    migrate_processes = False
    migrate_tasks = False
    migrate_usage_limits = False
    migrate_rag_assistants = False
    migrate_files = False
    
    agent_ids = None
    tool_ids = None
    process_ids = None
    task_ids = None
    assistant_names = None
    file_ids = None
    
    stop_on_error = True

    for option_flag, option_arg in option_list:
        if option_flag.name == "from_api_key":
            from_api_key = option_arg
        elif option_flag.name == "from_organization_api_key":
            from_organization_api_key = option_arg
        elif option_flag.name == "from_instance":
            from_instance = option_arg
        elif option_flag.name == "from_project_id":
            from_project_id = option_arg
        elif option_flag.name == "from_organization_id":
            from_organization_id = option_arg
        elif option_flag.name == "to_api_key":
            to_api_key = option_arg
        elif option_flag.name == "to_organization_api_key":
            to_organization_api_key = option_arg
        elif option_flag.name == "to_instance":
            to_instance = option_arg
        elif option_flag.name == "to_project_id":
            to_project_id = option_arg
        elif option_flag.name == "to_organization_id":
            to_organization_id = option_arg
        elif option_flag.name == "to_project_name":
            to_project_name = option_arg
        elif option_flag.name == "admin_email":
            admin_email = option_arg
        elif option_flag.name == "all":
            migrate_all = True
        elif option_flag.name == "agents":
            migrate_agents = True
            agent_ids = option_arg if option_arg else "all"
        elif option_flag.name == "tools":
            migrate_tools = True
            tool_ids = option_arg if option_arg else "all"
        elif option_flag.name == "agentic_processes":
            migrate_processes = True
            process_ids = option_arg if option_arg else "all"
        elif option_flag.name == "tasks":
            migrate_tasks = True
            task_ids = option_arg if option_arg else "all"
        elif option_flag.name == "usage_limits":
            migrate_usage_limits = True
        elif option_flag.name == "rag_assistants":
            migrate_rag_assistants = True
            assistant_names = option_arg if option_arg else "all"
        elif option_flag.name == "files":
            migrate_files = True
            file_ids = option_arg if option_arg else "all"
        elif option_flag.name == "stop_on_error":
            from pygeai.cli.commands.common import get_boolean_value
            stop_on_error = get_boolean_value(option_arg)

    if not all([from_api_key, from_instance, from_project_id]):
        raise MissingRequirementException("Source API key, instance, and project ID are required")

    if (to_project_name or admin_email) and not (to_project_name and admin_email):
        raise MissingRequirementException(
            "Both --to-project-name and --admin-email are required when creating a new project"
        )
    
    if to_project_id and (to_project_name or admin_email):
        raise MissingRequirementException(
            "Cannot specify both --to-project-id and project creation parameters (--to-project-name, --admin-email)"
        )
    
    if not to_project_id and not (to_project_name and admin_email):
        raise MissingRequirementException(
            "Must specify either --to-project-id (for existing project) or both --to-project-name and --admin-email (to create new project)"
        )
    
    if to_project_id and not to_api_key:
        raise MissingRequirementException(
            "Destination project API key (--to-api-key) is required when migrating to an existing project (--to-project-id)"
        )
    
    if to_project_name and admin_email:
        if not from_organization_api_key:
            raise MissingRequirementException(
                "Source organization scope API key (--from-org-key) is required for project creation"
            )
        if not (to_organization_api_key or from_organization_api_key):
            raise MissingRequirementException(
                "Destination organization scope API key (--to-org-key) is required for project creation in a different "
                "instance. Alternatively source organization scope (--from-org-key) can be used if project needs to be "
                "created in the same instance."
            )

    # Validate organization scope keys for usage limits migration
    if migrate_usage_limits:
        if not from_organization_api_key:
            raise MissingRequirementException(
                "Source organization scope API key (--from-org-key) is required for usage limits migration"
            )
        if not (to_organization_api_key or from_organization_api_key):
            raise MissingRequirementException(
                "Destination organization scope API key (--to-org-key) is required for usage limits migration in a "
                "different instance. Alternatively source organization scope (--from-org-key) can be used if limits "
                "need to be migrated in the same instance."
            )

    if to_project_name and admin_email:
        Console.write_stdout(f"Creating new project '{to_project_name}'...")
        
        org_key_to_use = to_organization_api_key or from_organization_api_key
        logger.debug(f"DEBUG: Preparing to create project with organization API key")
        logger.debug(f"  - to_organization_api_key exists: {to_organization_api_key is not None}")
        logger.debug(f"  - from_organization_api_key exists: {from_organization_api_key is not None}")
        logger.debug(f"  - Using key (first 20 chars): {org_key_to_use[:20] if org_key_to_use else 'None'}...")
        Console.write_stderr(f"DEBUG: Using org key for project creation (first 20 chars): {org_key_to_use[:20] if org_key_to_use else 'None'}...")
        
        project_strategy = ProjectMigrationStrategy(
            from_api_key=from_organization_api_key,
            from_instance=from_instance,
            from_project_id=from_project_id,
            to_project_name=to_project_name,
            admin_email=admin_email,
            to_api_key=org_key_to_use,
            to_instance=to_instance
        )
        project_tool = MigrationTool(project_strategy)
        to_project_id = project_tool.run_migration()
        
        if not to_project_id:
            raise ValueError("Project creation did not return a project ID")
        
        Console.write_stdout(f"Project '{to_project_name}' created successfully with ID: {to_project_id}")
        
        from pygeai.auth.clients import AuthClient
        Console.write_stdout(f"Creating project API key for new project...")
        
        org_key_for_token_creation = to_organization_api_key or from_organization_api_key
        auth_client = AuthClient(
            api_key=org_key_for_token_creation,
            base_url=to_instance or from_instance
        )
        
        token_response = auth_client.create_project_api_token(
            project_id=to_project_id,
            name=f"Migration API Key for {to_project_name}",
            description=f"Auto-generated API key for project migration to {to_project_name}"
        )
        
        if not token_response or 'id' not in token_response:
            raise ValueError("Failed to create project API key")
        
        to_api_key = token_response['id']
        Console.write_stdout(f"Project API key created successfully")
        
        if not to_organization_id:
            Console.write_stdout(f"Retrieving destination organization ID...")
            dest_admin_client = AdminClient(api_key=to_api_key, base_url=to_instance or from_instance)
            dest_token_info = dest_admin_client.validate_api_token()
            to_organization_id = dest_token_info.get("organizationId")
            Console.write_stdout(f"Destination organization ID: {to_organization_id}")

    if migrate_all:
        migrate_agents = True
        migrate_tools = True
        migrate_processes = True
        migrate_tasks = True
        migrate_usage_limits = True if from_organization_id and to_organization_id else False
        migrate_rag_assistants = True
        migrate_files = True if from_organization_id and to_organization_id else False
        agent_ids = "all"
        tool_ids = "all"
        process_ids = "all"
        task_ids = "all"
        assistant_names = "all"
        file_ids = "all"

    strategies = []
    
    lab_manager = AILabManager(api_key=from_api_key, base_url=from_instance)

    if migrate_agents:
        if agent_ids == "all":
            agent_list = lab_manager.get_agent_list(FilterSettings(count=1000))
            discovered_agents = [agent.id for agent in agent_list.agents if agent.id]
            Console.write_stdout(f"Discovered {len(discovered_agents)} agents")
            for agent_id in discovered_agents:
                strategies.append(AgentMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    agent_id=agent_id,
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
        elif agent_ids:
            for agent_id in agent_ids.split(','):
                strategies.append(AgentMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    agent_id=agent_id.strip(),
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
    
    if migrate_tools:
        if tool_ids == "all":
            tool_list = lab_manager.list_tools(FilterSettings(count=1000))
            discovered_tools = [tool.id for tool in tool_list.tools if tool.id]
            Console.write_stdout(f"Discovered {len(discovered_tools)} tools")
            for tool_id in discovered_tools:
                strategies.append(ToolMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    tool_id=tool_id,
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
        elif tool_ids:
            for tool_id in tool_ids.split(','):
                strategies.append(ToolMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    tool_id=tool_id.strip(),
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
    
    if migrate_processes:
        if process_ids == "all":
            process_list = lab_manager.list_processes(FilterSettings(count=1000))
            discovered_processes = [proc.id for proc in process_list.processes if proc.id]
            Console.write_stdout(f"Discovered {len(discovered_processes)} agentic processes")
            for process_id in discovered_processes:
                strategies.append(AgenticProcessMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    process_id=process_id,
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
        elif process_ids:
            for process_id in process_ids.split(','):
                strategies.append(AgenticProcessMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    process_id=process_id.strip(),
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
    
    if migrate_tasks:
        if task_ids == "all":
            task_list = lab_manager.list_tasks(FilterSettings(count=1000))
            discovered_tasks = [task.id for task in task_list.tasks if task.id]
            Console.write_stdout(f"Discovered {len(discovered_tasks)} tasks")
            for task_id in discovered_tasks:
                strategies.append(TaskMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    task_id=task_id,
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
        elif task_ids:
            for task_id in task_ids.split(','):
                strategies.append(TaskMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    task_id=task_id.strip(),
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
    
    if migrate_usage_limits and from_organization_id and to_organization_id:
        strategies.append(UsageLimitMigrationStrategy(
            from_api_key=from_organization_api_key,
            from_instance=from_instance,
            from_organization_id=from_organization_id,
            to_organization_id=to_organization_id,
            to_api_key=to_organization_api_key or from_organization_api_key,
            to_instance=to_instance
        ))
    
    if migrate_rag_assistants:
        rag_client = RAGAssistantClient(api_key=from_api_key, base_url=from_instance)
        if assistant_names == "all":
            assistant_data = rag_client.get_assistants_from_project()
            assistants_raw = assistant_data.get("assistants", [])
            assistant_list = [RAGAssistantMapper.map_to_rag_assistant(a) for a in assistants_raw] if assistants_raw else []
            discovered_assistants = [assistant.name for assistant in assistant_list if assistant.name]
            Console.write_stdout(f"Discovered {len(discovered_assistants)} RAG assistants")
            for assistant_name in discovered_assistants:
                strategies.append(RAGAssistantMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    assistant_name=assistant_name,
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
        elif assistant_names:
            for assistant_name in assistant_names.split(','):
                strategies.append(RAGAssistantMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    assistant_name=assistant_name.strip(),
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
    
    if migrate_files and from_organization_id and from_project_id and to_organization_id and to_project_id:
        file_manager = FileManager(
            api_key=from_api_key,
            base_url=from_instance,
            organization_id=from_organization_id,
            project_id=from_project_id
        )
        if file_ids == "all":
            file_list_response = file_manager.get_file_list()
            discovered_files = [f.id for f in file_list_response.files if f.id]
            Console.write_stdout(f"Discovered {len(discovered_files)} files")
            for file_id in discovered_files:
                strategies.append(FileMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    from_organization_id=from_organization_id,
                    from_project_id=from_project_id,
                    to_organization_id=to_organization_id,
                    to_project_id=to_project_id,
                    file_id=file_id,
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))
        elif file_ids:
            for file_id in file_ids.split(','):
                strategies.append(FileMigrationStrategy(
                    from_api_key=from_api_key,
                    from_instance=from_instance,
                    from_organization_id=from_organization_id,
                    from_project_id=from_project_id,
                    to_organization_id=to_organization_id,
                    to_project_id=to_project_id,
                    file_id=file_id.strip(),
                    to_api_key=to_api_key,
                    to_instance=to_instance
                ))

    if not strategies:
        Console.write_stdout("No migration strategies configured. Use flags like --agents, --tools, --all, etc.")
        return

    plan = MigrationPlan(strategies=strategies, stop_on_error=stop_on_error)
    orchestrator = MigrationOrchestrator(plan)
    
    try:
        result = orchestrator.execute()
        Console.write_stdout(f"Migration completed: {result['completed']}/{result['total']} successful")
        logger.info(f"Project cloning completed: {result}")
    except Exception as e:
        Console.write_stderr(f"Migration failed: {e}")
        logger.error(f"Project cloning failed: {e}")
        raise


clone_project_options = [
    Option(
        "interactive",
        ["-i", "--interactive"],
        "Interactive mode: guided step-by-step migration wizard",
        False
    ),
    Option(
        "from_api_key",
        ["--from-api-key", "--from-key"],
        "Source instance project scope API key (required)",
        True
    ),
    Option(
        "from_organization_api_key",
        ["--from-org-key", "--from-organization-key"],
        "Source instance organization scope API key (optional, for project creation)",
        True
    ),
    Option(
        "from_instance",
        ["--from-instance", "--from-url"],
        "Source instance URL (required)",
        True
    ),
    Option(
        "from_project_id",
        ["--from-project-id", "--from-pid"],
        "Source project ID (required)",
        True
    ),
    Option(
        "from_organization_id",
        ["--from-organization-id", "--from-oid"],
        "Source organization ID (required for usage limits and files)",
        True
    ),
    Option(
        "to_api_key",
        ["--to-api-key", "--to-key"],
        "Destination instance project scope API key (optional, defaults to source key)",
        True
    ),
    Option(
        "to_organization_api_key",
        ["--to-org-key", "--to-organization-key"],
        "Destination instance organization scope API key (optional, for project creation)",
        True
    ),
    Option(
        "to_instance",
        ["--to-instance", "--to-url"],
        "Destination instance URL (optional, defaults to source URL)",
        True
    ),
    Option(
        "to_project_name",
        ["--to-project-name", "--to-name"],
        "Name for the new destination project (creates new project if specified with --admin-email)",
        True
    ),
    Option(
        "admin_email",
        ["--admin-email"],
        "Admin email for new project (required when creating new project)",
        True
    ),
    Option(
        "to_project_id",
        ["--to-project-id", "--to-pid"],
        "Destination project ID (optional for files)",
        True
    ),
    Option(
        "to_organization_id",
        ["--to-organization-id", "--to-oid"],
        "Destination organization ID (optional for usage limits and files)",
        True
    ),
    Option(
        "all",
        ["--all"],
        "Migrate all available components",
        False
    ),
    Option(
        "agents",
        ["--agents"],
        "Agent IDs to migrate: comma-separated IDs or 'all'",
        True
    ),
    Option(
        "tools",
        ["--tools"],
        "Tool IDs to migrate: comma-separated IDs or 'all'",
        True
    ),
    Option(
        "agentic_processes",
        ["--agentic-processes", "--processes"],
        "Agentic process IDs to migrate: comma-separated IDs or 'all'",
        True
    ),
    Option(
        "tasks",
        ["--tasks"],
        "Task IDs to migrate: comma-separated IDs or 'all'",
        True
    ),
    Option(
        "usage_limits",
        ["--usage-limits"],
        "Migrate usage limits (requires organization IDs)",
        False
    ),
    Option(
        "rag_assistants",
        ["--rag-assistants"],
        "RAG assistant names to migrate: comma-separated names or 'all'",
        True
    ),
    Option(
        "files",
        ["--files"],
        "File IDs to migrate: comma-separated IDs or 'all' (requires org/project IDs)",
        True
    ),
    Option(
        "stop_on_error",
        ["--stop-on-error", "--soe"],
        "Stop migration on first error: 0: False, 1: True (default: 1)",
        True
    ),
]


migrate_commands = [
    Command(
        "help",
        ["help", "h"],
        "Display help text",
        show_help,
        ArgumentsEnum.NOT_AVAILABLE,
        [],
        []
    ),
    Command(
        "clone_project",
        ["clone-project"],
        "Clone project components between instances",
        clone_project,
        ArgumentsEnum.REQUIRED,
        [],
        clone_project_options
    ),
]
