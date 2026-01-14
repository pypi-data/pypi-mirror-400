import traceback
from difflib import SequenceMatcher
from typing import List, Optional

from pygeai import logger
from pygeai.cli.commands import Command, Option
from pygeai.core.utils.console import Console


class ExitCode:
    SUCCESS = 0
    USER_INPUT_ERROR = 1
    MISSING_REQUIREMENT = 2
    SERVICE_ERROR = 3
    KEYBOARD_INTERRUPT = 130
    UNEXPECTED_ERROR = 255


class ErrorHandler:

    @staticmethod
    def format_error(error_type: str, message: str, suggestion: Optional[str] = None, show_help: bool = True) -> str:
        output = f"ERROR: {message}"
        
        if suggestion:
            output += f"\n  → {suggestion}"
        
        if show_help:
            output += "\n\nRun 'geai help' for usage information."
        
        return output

    @staticmethod
    def find_similar_items(item: str, available_items: List[str], threshold: float = 0.6) -> List[str]:
        similarities = []
        for available in available_items:
            ratio = SequenceMatcher(None, item.lower(), available.lower()).ratio()
            if ratio >= threshold:
                similarities.append((available, ratio))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in similarities[:3]]

    @staticmethod
    def get_available_commands(commands: List[Command]) -> List[str]:
        all_identifiers = []
        for cmd in commands:
            all_identifiers.extend(cmd.identifiers)
        return all_identifiers

    @staticmethod
    def get_available_options(options: List[Option]) -> List[str]:
        all_identifiers = []
        for opt in options:
            all_identifiers.extend(opt.identifiers)
        return all_identifiers

    @staticmethod
    def handle_unknown_command(command: str, available_commands: List[Command]) -> str:
        cmd_identifiers = ErrorHandler.get_available_commands(available_commands)
        similar = ErrorHandler.find_similar_items(command, cmd_identifiers)
        
        message = f"'{command}' is not a valid command."
        
        if similar:
            suggestion = f"Did you mean: {', '.join(similar)}?"
        else:
            suggestion = f"Available commands: {', '.join(sorted(set([cmd.identifiers[0] for cmd in available_commands])))}"
        
        return ErrorHandler.format_error("Unknown Command", message, suggestion)

    @staticmethod
    def handle_unknown_option(option: str, available_options: List[Option]) -> str:
        opt_identifiers = ErrorHandler.get_available_options(available_options)
        similar = ErrorHandler.find_similar_items(option, opt_identifiers)
        
        message = f"'{option}' is not a valid option."
        
        if similar:
            suggestion = f"Did you mean: {', '.join(similar)}?"
        else:
            suggestion = f"Available options: {', '.join(sorted(set([opt.identifiers[0] for opt in available_options])))}"
        
        return ErrorHandler.format_error("Unknown Option", message, suggestion)

    @staticmethod
    def handle_missing_requirement(requirement_message: str) -> str:
        message = requirement_message
        suggestion = "Please provide all required parameters."
        return ErrorHandler.format_error("Missing Requirement", message, suggestion)

    @staticmethod
    def handle_invalid_agent(error_message: str) -> str:
        message = f"Failed to retrieve or validate the agent.\n  Details: {error_message}"
        suggestion = "Check your agent configuration and ensure the agent exists."
        return ErrorHandler.format_error("Invalid Agent", message, suggestion)

    @staticmethod
    def handle_wrong_argument(error_message: str, usage: str) -> str:
        Console.write_stderr(f"usage: {usage}")
        message = error_message
        suggestion = "Check the command syntax and try again."
        return ErrorHandler.format_error("Invalid Argument", message, suggestion)

    @staticmethod
    def handle_keyboard_interrupt() -> str:
        return "\n\nOperation cancelled by user."

    @staticmethod
    def handle_unexpected_error(exception: Exception) -> str:
        logger.error(f"Unexpected error occurred: {exception}")
        logger.error(traceback.format_exc())
        
        message = "An unexpected error occurred. This may be a bug."
        suggestion = f"Please report this issue to geai-sdk@globant.com with the following details:\n  Error: {str(exception)}\n  Check logs for full traceback."
        return ErrorHandler.format_error("Critical Error", message, suggestion, show_help=False)
