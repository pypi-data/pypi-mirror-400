import sys

from pygeai import logger
from pygeai.cli.commands.base import base_commands, base_options
from pygeai.cli.commands import ArgumentsEnum, Command
from pygeai.cli.parsers import CommandParser
from pygeai.cli.texts.help import CLI_USAGE
from pygeai.cli.error_handler import ErrorHandler, ExitCode
from pygeai.core.base.session import get_session
from pygeai.core.common.exceptions import UnknownArgumentError, MissingRequirementException, WrongArgumentError, \
    InvalidAgentException
from pygeai.core.utils.console import Console


def main():
    driver = CLIDriver()
    return driver.main()


class CLIDriver:

    def __init__(self, session=None):
        """
        Sets session to be used while running the command, either with a specified alias,
        environment variables or function parameters.
        Once the session is defined, it won't change during the curse of the execution.
        """
        arguments = sys.argv
        if "-a" in arguments or "--alias" in arguments:
            alias = self._get_alias(arguments)
            session = get_session(alias)

        self.session = get_session("default") if session is None else session

    def _get_alias(self, arguments: list):
        """
        Retrieves and removes alias and alias flag from argument list
        """
        alias_index = None

        if "-a" in arguments:
            alias_index = arguments.index("-a")
        elif "--alias" in arguments:
            alias_index = arguments.index("--alias")

        _ = arguments.pop(alias_index)
        alias = arguments.pop(alias_index)
        return alias

    def main(self, args=None):
        """
        If not argument is received, it defaults to help (first command in base_command list).
        Otherwise, it parses the arguments received to identify the appropriate command and either
        execute it or parse it again to detect subcommands.
        """
        try:
            logger.debug(f"Running geai with: {' '.join(a for a in sys.argv)}")
            if len(sys.argv) > 1:
                arg = sys.argv[1] if args is None else args[1]
                arguments = sys.argv[2:] if args is None else args[2:]

                command = CommandParser(base_commands, base_options).identify_command(arg)
            else:
                command = base_commands[0]
                arguments = []

            self.process_command(command, arguments)
            return ExitCode.SUCCESS
        except UnknownArgumentError as e:
            if hasattr(e, 'available_commands') and e.available_commands:
                error_msg = ErrorHandler.handle_unknown_command(e.arg, e.available_commands)
            elif hasattr(e, 'available_options') and e.available_options:
                error_msg = ErrorHandler.handle_unknown_option(e.arg, e.available_options)
            else:
                error_msg = ErrorHandler.format_error("Unknown Argument", str(e))
            
            Console.write_stderr(error_msg)
            return ExitCode.USER_INPUT_ERROR
        except WrongArgumentError as e:
            error_msg = ErrorHandler.handle_wrong_argument(str(e), CLI_USAGE)
            Console.write_stderr(error_msg)
            return ExitCode.USER_INPUT_ERROR
        except MissingRequirementException as e:
            error_msg = ErrorHandler.handle_missing_requirement(str(e))
            Console.write_stderr(error_msg)
            return ExitCode.MISSING_REQUIREMENT
        except InvalidAgentException as e:
            error_msg = ErrorHandler.handle_invalid_agent(str(e))
            Console.write_stderr(error_msg)
            return ExitCode.SERVICE_ERROR
        except KeyboardInterrupt:
            message = ErrorHandler.handle_keyboard_interrupt()
            Console.write_stdout(message)
            return ExitCode.KEYBOARD_INTERRUPT
        except Exception as e:
            error_msg = ErrorHandler.handle_unexpected_error(e)
            Console.write_stderr(error_msg)
            return ExitCode.UNEXPECTED_ERROR

    def process_command(self, command: Command, arguments: list[str]):
        """
        If the command has no action associated with it, it means it has subcommands, so it must be parsed again
        to identify it.
        """
        if command.action:
            if command.additional_args == ArgumentsEnum.NOT_AVAILABLE:
                command.action()
            else:
                option_list = CommandParser(base_commands, command.options).extract_option_list(arguments)
                command.action(option_list)
        elif command.subcommands:
            subcommand_arg = arguments[0] if len(arguments) > 0 else None
            subcommand_arguments = arguments[1:] if len(arguments) > 1 else []

            available_commands = command.subcommands
            available_options = command.options
            parser = CommandParser(available_commands, available_options)

            if not subcommand_arg:
                subcommand = command.subcommands[0]
            else:
                subcommand = parser.identify_command(subcommand_arg)

            if subcommand.additional_args == ArgumentsEnum.NOT_AVAILABLE:
                subcommand.action()
            else:
                option_list = CommandParser(None, subcommand.options).extract_option_list(subcommand_arguments)
                subcommand.action(option_list)
