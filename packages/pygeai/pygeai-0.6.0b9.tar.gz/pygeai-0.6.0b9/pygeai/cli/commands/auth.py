from pygeai.auth.clients import AuthClient
from pygeai.cli.commands import Command, Option, ArgumentsEnum
from pygeai.cli.commands.builders import build_help_text
from pygeai.cli.texts.help import AUTH_HELP_TEXT
from pygeai.core.common.exceptions import MissingRequirementException, WrongArgumentError
from pygeai.core.utils.console import Console


def show_help():
    """
    Displays help text in stdout
    """
    help_text = build_help_text(auth_commands, AUTH_HELP_TEXT)
    Console.write_stdout(help_text)


def get_oauth2_access_token(option_list: list):
    client_id = None
    username = None
    password = None
    scope = "gam_user_data gam_user_roles"
    for option_flag, option_arg in option_list:
        if option_flag.name == "client_id":
            client_id = option_arg
        if option_flag.name == "username":
            username = option_arg
        if option_flag.name == "password":
            password = option_arg
        if option_flag.name == "scope":
            scope = option_arg

    if not (client_id and username and password):
        raise MissingRequirementException("Cannot obtain Oauth2 access token without client_id, username and password")

    client = AuthClient()
    result = client.get_oauth2_access_token(
        client_id=client_id,
        username=username,
        password=password,
        scope=scope
    )
    Console.write_stdout(f"Authorized projects detail: \n{result}")


get_oauth2_access_token_options = [
    Option(
        "client_id",
        ["--client-id", "--cid"],
        "The client identifier provided by Globant.",
        True
    ),
    Option(
        "username",
        ["--username", "-u"],
        "Username for authentication.",
        True
    ),
    Option(
        "password",
        ["--password", "-p"],
        "Password for authentication.",
        True
    ),
    Option(
        "scope",
        ["--scope", "-s"],
        "Space-separated list of requested scopes. (Optional)",
        True
    ),

]


def get_user_profile_information(option_list: list):
    access_token = None
    for option_flag, option_arg in option_list:
        if option_flag.name == "access_token":
            access_token = option_arg

    client = AuthClient()
    result = client.get_user_profile_information(access_token=access_token)
    Console.write_stdout(f"User profile information: \n{result}")


get_user_profile_information_options = [
    Option(
        "access_token",
        ["--access-token", "--token"],
        "Token obtained with the --get-access-token option",
        True
    ),
]


def create_project_api_token(option_list: list):
    project_id = None
    name = None
    description = None
    for option_flag, option_arg in option_list:
        if option_flag.name == "project_id":
            project_id = option_arg
        if option_flag.name == "name":
            name = option_arg
        if option_flag.name == "description":
            description = option_arg

    if not (project_id and name):
        raise MissingRequirementException("Cannot create project API token without project-id and name")

    client = AuthClient()
    result = client.create_project_api_token(
        project_id=project_id,
        name=name,
        description=description
    )
    Console.write_stdout(f"Project API token created: \n{result}")


create_project_api_token_options = [
    Option(
        "project_id",
        ["--project-id", "--pid"],
        "The project identifier (required).",
        True
    ),
    Option(
        "name",
        ["--name", "-n"],
        "The name of the API token (required).",
        True
    ),
    Option(
        "description",
        ["--description", "-d"],
        "A description of the API token (optional).",
        True
    ),
]


def delete_project_api_token(option_list: list):
    api_token_id = None
    for option_flag, option_arg in option_list:
        if option_flag.name == "api_token_id":
            api_token_id = option_arg

    if not api_token_id:
        raise MissingRequirementException("Cannot delete project API token without api-token-id")

    client = AuthClient()
    result = client.delete_project_api_token(api_token_id=api_token_id)
    Console.write_stdout(f"Project API token deleted: \n{result}")


delete_project_api_token_options = [
    Option(
        "api_token_id",
        ["--api-token-id", "--tid"],
        "The unique identifier of the API token to delete (required).",
        True
    ),
]


def update_project_api_token(option_list: list):
    api_token_id = None
    description = None
    status = None
    for option_flag, option_arg in option_list:
        if option_flag.name == "api_token_id":
            api_token_id = option_arg
        if option_flag.name == "description":
            description = option_arg
        if option_flag.name == "status":
            status = option_arg

    if not api_token_id:
        raise MissingRequirementException("Cannot update project API token without api-token-id")

    client = AuthClient()
    result = client.update_project_api_token(
        api_token_id=api_token_id,
        description=description,
        status=status
    )
    Console.write_stdout(f"Project API token updated: \n{result}")


update_project_api_token_options = [
    Option(
        "api_token_id",
        ["--api-token-id", "--tid"],
        "The unique identifier of the API token to update (required).",
        True
    ),
    Option(
        "description",
        ["--description", "-d"],
        "A new description for the API token (optional).",
        True
    ),
    Option(
        "status",
        ["--status"],
        "The new status for the API token: 'active' or 'blocked' (optional).",
        True
    ),
]


def get_project_api_token(option_list: list):
    api_token_id = None
    for option_flag, option_arg in option_list:
        if option_flag.name == "api_token_id":
            api_token_id = option_arg

    if not api_token_id:
        raise MissingRequirementException("Cannot get project API token without api-token-id")

    client = AuthClient()
    result = client.get_project_api_token(api_token_id=api_token_id)
    Console.write_stdout(f"Project API token details: \n{result}")


get_project_api_token_options = [
    Option(
        "api_token_id",
        ["--api-token-id", "--tid"],
        "The unique identifier of the API token (required).",
        True
    ),
]


auth_commands = [
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
        "get_oauth2_access_token",
        ["get-access-token", "gat"],
        "Get Oauth acess token for Globant Enterprise AI instance",
        get_oauth2_access_token,
        ArgumentsEnum.REQUIRED,
        [],
        get_oauth2_access_token_options
    ),
    Command(
        "get_user_profile_information",
        ["get-user-information", "get-user-info", "gui"],
        "Retrieve user profile information",
        get_user_profile_information,
        ArgumentsEnum.REQUIRED,
        [],
        get_user_profile_information_options
    ),
    Command(
        "create_project_api_token",
        ["create-project-api-token", "create-api-token", "cat"],
        "Create a new API token for a project",
        create_project_api_token,
        ArgumentsEnum.REQUIRED,
        [],
        create_project_api_token_options
    ),
    Command(
        "delete_project_api_token",
        ["delete-project-api-token", "delete-api-token", "dat"],
        "Revoke an API token",
        delete_project_api_token,
        ArgumentsEnum.REQUIRED,
        [],
        delete_project_api_token_options
    ),
    Command(
        "update_project_api_token",
        ["update-project-api-token", "update-api-token", "uat"],
        "Update an existing API token",
        update_project_api_token,
        ArgumentsEnum.REQUIRED,
        [],
        update_project_api_token_options
    ),
    Command(
        "get_project_api_token",
        ["get-project-api-token", "get-api-token", "gat"],
        "Get data of a specific project API token",
        get_project_api_token,
        ArgumentsEnum.REQUIRED,
        [],
        get_project_api_token_options
    ),
]
