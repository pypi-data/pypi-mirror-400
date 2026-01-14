import json
from pygeai.cli.commands import Command, Option, ArgumentsEnum
from pygeai.cli.commands.builders import build_help_text
from pygeai.cli.commands.common import get_boolean_value
from pygeai.cli.texts.help import EMBEDDINGS_HELP_TEXT
from pygeai.core.common.exceptions import MissingRequirementException, WrongArgumentError
from pygeai.core.embeddings.clients import EmbeddingsClient
from pygeai.core.utils.console import Console


def show_help():
    """
    Displays help text in stdout
    """
    help_text = build_help_text(embeddings_commands, EMBEDDINGS_HELP_TEXT)
    Console.write_stdout(help_text)


def generate_embeddings(option_list: list):
    model = None
    encoding_format = None
    dimensions = None
    user = None
    input_type = None
    timeout = None
    cache = None
    preview = True
    input_list = list()

    for option_flag, option_arg in option_list:
        if option_flag.name == "model":
            model = option_arg
        if option_flag.name == "input":
            input_list.append(option_arg)
        if option_flag.name == "encoding_format":
            encoding_format = option_arg
        if option_flag.name == "dimensions":
            try:
                dimensions = int(option_arg)
            except (ValueError, TypeError):
                raise WrongArgumentError("dimensions must be an integer")
        if option_flag.name == "user":
            user = option_arg
        if option_flag.name == "input_type":
            input_type = option_arg
        if option_flag.name == "timeout":
            try:
                timeout = int(option_arg)
            except (ValueError, TypeError):
                raise WrongArgumentError("timeout must be an integer")
        if option_flag.name == "cache":
            cache = get_boolean_value(option_arg)
        if option_flag.name == "preview":
            preview = get_boolean_value(option_arg)

    if not (model and any(input_list)):
        raise MissingRequirementException("Cannot generate embeddings without specifying model and at least one input")

    client = EmbeddingsClient()
    result = client.generate_embeddings(
        input_list=input_list,
        model=model,
        encoding_format=encoding_format,
        dimensions=dimensions,
        user=user,
        input_type=input_type,
        timeout=timeout,
        cache=cache
    )
    
    output = {
        "model": result.get("model"),
        "object": result.get("object"),
        "embeddings_count": len(result.get("data", [])),
        "usage": result.get("usage"),
        "data": []
    }
    
    for item in result.get("data", []):
        embedding_data = item.get("embedding")
        if isinstance(embedding_data, list):
            embedding_info = {
                "index": item.get("index"),
                "dimensions": len(embedding_data),
                "object": item.get("object")
            }
            if preview:
                embedding_info["preview"] = embedding_data[:5] if len(embedding_data) > 5 else embedding_data
            else:
                embedding_info["embedding"] = embedding_data
        else:
            embedding_info = {
                "index": item.get("index"),
                "object": item.get("object"),
                "format": "base64"
            }
            if preview:
                embedding_info["preview"] = str(embedding_data)[:50] + "..." if len(str(embedding_data)) > 50 else embedding_data
            else:
                embedding_info["embedding"] = embedding_data
        output["data"].append(embedding_info)
    
    Console.write_stdout(json.dumps(output, indent=2))


generate_embeddings_options = [
    Option(
        "input",
        ["--input", "-i"],
        "string: Input to embed, encoded as a string. To embed multiple inputs in a single request, pass the string inputs "
        "multiple times using -i. The input must not exceed the max input tokens for the model and cannot be an empty string",
        True
    ),
    Option(
        "model",
        ["--model", "-m"],
        "string: provider/modelId to use",
        True
    ),
    Option(
        "encoding_format",
        ["--encoding-format", "--enc-for"],
        "string: The format to return the embeddings. It can be either float (default) or base64 (optional)",
        True
    ),
    Option(
        "dimensions",
        ["--dimensions", "--dim"],
        "integer: The number of dimensions the resulting output embeddings should have. Only supported in text-embedding-3* and later models (optional)",
        True
    ),
    Option(
        "user",
        ["--user", "-u"],
        "string: A unique identifier representing your end-user",
        True
    ),
    Option(
        "input_type",
        ["--input-type", "--it"],
        "string: Defines how the input data will be used when generating embeddings (optional)",
        True
    ),
    Option(
        "timeout",
        ["--timeout", "-t"],
        "integer: The maximum time, in seconds, to wait for the API to respond. Defaults to 600 seconds",
        True
    ),
    Option(
        "cache",
        ["--cache"],
        "Enable X-Saia-Cache-Enabled to cache the embeddings for the model; it applies by Organization/Project. "
        "1 to set to True and 0 to false. 0 is default",
        True
    ),
    Option(
        "preview",
        ["--preview"],
        "Control embedding display in output. 1 (default) shows a preview (first 5 values for float, 50 chars for base64). "
        "0 shows the full embedding vector. Use 0 to get complete embeddings for further processing",
        True
    ),

]


embeddings_commands = [
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
        "generate_embeddings",
        ["generate", "gen"],
        "Get embeddings",
        generate_embeddings,
        ArgumentsEnum.REQUIRED,
        [],
        generate_embeddings_options
    ),
]
