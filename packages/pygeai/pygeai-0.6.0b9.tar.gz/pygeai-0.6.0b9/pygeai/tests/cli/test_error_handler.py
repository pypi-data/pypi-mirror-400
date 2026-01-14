import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from pygeai.cli.commands import Command, Option, ArgumentsEnum
from pygeai.cli.error_handler import ErrorHandler, ExitCode


class TestErrorHandler(TestCase):
    """
    Test suite for the ErrorHandler class.
    Run with: python -m unittest pygeai.tests.cli.test_error_handler.TestErrorHandler
    """

    def setUp(self):
        self.commands = [
            Command(
                name='help',
                identifiers=['help', 'h'],
                description='Display help',
                action=None,
                additional_args=ArgumentsEnum.NOT_AVAILABLE,
                subcommands=[],
                options=[]
            ),
            Command(
                name='version',
                identifiers=['version', 'v'],
                description='Display version',
                action=None,
                additional_args=ArgumentsEnum.NOT_AVAILABLE,
                subcommands=[],
                options=[]
            ),
            Command(
                name='configure',
                identifiers=['configure', 'config', 'c'],
                description='Configure settings',
                action=None,
                additional_args=ArgumentsEnum.OPTIONAL,
                subcommands=[],
                options=[]
            ),
        ]

        self.options = [
            Option(
                name='key',
                identifiers=['--key', '-k'],
                description='API key',
                requires_args=True
            ),
            Option(
                name='url',
                identifiers=['--url', '-u'],
                description='API URL',
                requires_args=True
            ),
        ]

    def test_exit_codes_defined(self):
        """Test that all exit codes are properly defined"""
        self.assertEqual(ExitCode.SUCCESS, 0)
        self.assertEqual(ExitCode.USER_INPUT_ERROR, 1)
        self.assertEqual(ExitCode.MISSING_REQUIREMENT, 2)
        self.assertEqual(ExitCode.SERVICE_ERROR, 3)
        self.assertEqual(ExitCode.KEYBOARD_INTERRUPT, 130)
        self.assertEqual(ExitCode.UNEXPECTED_ERROR, 255)

    def test_format_error_basic(self):
        """Test basic error formatting"""
        result = ErrorHandler.format_error("Test Error", "Something went wrong")
        self.assertIn("ERROR: Something went wrong", result)
        self.assertIn("Run 'geai help' for usage information.", result)

    def test_format_error_with_suggestion(self):
        """Test error formatting with suggestion"""
        result = ErrorHandler.format_error(
            "Test Error",
            "Command not found",
            suggestion="Try using 'help' command"
        )
        self.assertIn("ERROR: Command not found", result)
        self.assertIn("→ Try using 'help' command", result)

    def test_format_error_without_help(self):
        """Test error formatting without help text"""
        result = ErrorHandler.format_error(
            "Test Error",
            "Critical error",
            show_help=False
        )
        self.assertIn("ERROR: Critical error", result)
        self.assertNotIn("Run 'geai help'", result)

    def test_find_similar_items_exact_match(self):
        """Test fuzzy matching with high similarity"""
        items = ['help', 'version', 'configure']
        similar = ErrorHandler.find_similar_items('halp', items)
        self.assertIn('help', similar)

    def test_find_similar_items_no_match(self):
        """Test fuzzy matching with no similar items"""
        items = ['help', 'version', 'configure']
        similar = ErrorHandler.find_similar_items('xyz123', items, threshold=0.6)
        self.assertEqual(len(similar), 0)

    def test_find_similar_items_multiple_matches(self):
        """Test fuzzy matching returns top matches"""
        items = ['configure', 'config', 'configuration', 'help']
        similar = ErrorHandler.find_similar_items('config', items)
        self.assertGreater(len(similar), 0)
        self.assertLessEqual(len(similar), 3)

    def test_get_available_commands(self):
        """Test extraction of available command identifiers"""
        identifiers = ErrorHandler.get_available_commands(self.commands)
        self.assertIn('help', identifiers)
        self.assertIn('h', identifiers)
        self.assertIn('version', identifiers)
        self.assertIn('v', identifiers)
        self.assertIn('configure', identifiers)
        self.assertIn('config', identifiers)
        self.assertIn('c', identifiers)

    def test_get_available_options(self):
        """Test extraction of available option identifiers"""
        identifiers = ErrorHandler.get_available_options(self.options)
        self.assertIn('--key', identifiers)
        self.assertIn('-k', identifiers)
        self.assertIn('--url', identifiers)
        self.assertIn('-u', identifiers)

    def test_handle_unknown_command_with_fuzzy_match(self):
        """Test unknown command error with fuzzy matching suggestion"""
        result = ErrorHandler.handle_unknown_command('halp', self.commands)
        self.assertIn("'halp' is not a valid command", result)
        self.assertIn("Did you mean", result)
        self.assertIn("help", result)

    def test_handle_unknown_command_no_match(self):
        """Test unknown command error without fuzzy match"""
        result = ErrorHandler.handle_unknown_command('xyz123', self.commands)
        self.assertIn("'xyz123' is not a valid command", result)
        self.assertIn("Available commands:", result)

    def test_handle_unknown_option_with_fuzzy_match(self):
        """Test unknown option error with fuzzy matching"""
        result = ErrorHandler.handle_unknown_option('--kee', self.options)
        self.assertIn("'--kee' is not a valid option", result)
        self.assertIn("Did you mean", result)

    def test_handle_unknown_option_no_match(self):
        """Test unknown option error without fuzzy match"""
        result = ErrorHandler.handle_unknown_option('--completely-different-option-xyz123', self.options)
        self.assertIn("'--completely-different-option-xyz123' is not a valid option", result)
        self.assertIn("Available options:", result)

    def test_handle_missing_requirement(self):
        """Test missing requirement error formatting"""
        result = ErrorHandler.handle_missing_requirement("API key is required")
        self.assertIn("API key is required", result)
        self.assertIn("Please provide all required parameters", result)

    def test_handle_invalid_agent(self):
        """Test invalid agent error formatting"""
        result = ErrorHandler.handle_invalid_agent("Agent 'test-agent' not found")
        self.assertIn("Failed to retrieve or validate the agent", result)
        self.assertIn("Agent 'test-agent' not found", result)
        self.assertIn("Check your agent configuration", result)

    def test_handle_wrong_argument(self):
        """Test wrong argument error formatting"""
        usage = "geai <command> [options]"
        result = ErrorHandler.handle_wrong_argument("Invalid format", usage)
        self.assertIn("Invalid format", result)
        self.assertIn("Check the command syntax", result)

    def test_handle_keyboard_interrupt(self):
        """Test keyboard interrupt message"""
        result = ErrorHandler.handle_keyboard_interrupt()
        self.assertIn("Operation cancelled by user", result)

    def test_handle_unexpected_error(self):
        """Test unexpected error formatting"""
        exception = ValueError("Test error")
        result = ErrorHandler.handle_unexpected_error(exception)
        self.assertIn("unexpected error occurred", result)
        self.assertIn("Test error", result)
        self.assertIn("geai-sdk@globant.com", result)

    def test_fuzzy_matching_threshold(self):
        """Test that threshold parameter works correctly"""
        items = ['configure', 'help', 'version']
        
        # With high threshold, should not match
        similar_high = ErrorHandler.find_similar_items('xyz', items, threshold=0.9)
        self.assertEqual(len(similar_high), 0)
        
        # With low threshold, might match
        similar_low = ErrorHandler.find_similar_items('c', items, threshold=0.3)
        self.assertGreaterEqual(len(similar_low), 0)

    def test_multiple_command_identifiers_in_suggestions(self):
        """Test that fuzzy matching works with multiple identifiers"""
        result = ErrorHandler.handle_unknown_command('configurr', self.commands)
        # Should suggest 'configure' or 'config'
        self.assertTrue('configure' in result or 'config' in result)

    def test_error_format_consistency(self):
        """Test that all error handlers produce consistent format"""
        results = [
            ErrorHandler.handle_unknown_command('test', self.commands),
            ErrorHandler.handle_unknown_option('--test', self.options),
            ErrorHandler.handle_missing_requirement("test requirement"),
            ErrorHandler.handle_invalid_agent("test agent"),
        ]
        
        for result in results:
            self.assertIn("ERROR:", result)
            self.assertIn("→", result)


if __name__ == '__main__':
    unittest.main()
