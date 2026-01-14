import unittest
import sys
from unittest import TestCase
from unittest.mock import patch
from io import StringIO

from pygeai.cli.geai import CLIDriver
from pygeai.cli.error_handler import ExitCode


class TestCLIDriver(TestCase):
    """
    Test suite for CLIDriver error handling integration.
    Run with: python -m unittest pygeai.tests.cli.test_geai_driver.TestCLIDriver
    """

    def setUp(self):
        """Set up test fixtures"""
        self.driver = CLIDriver()

    @patch('sys.stderr', new_callable=StringIO)
    def test_unknown_command_exit_code(self, mock_stderr):
        """Test that unknown command returns correct exit code"""
        sys.argv = ['geai', 'unknown_command_xyz']
        exit_code = self.driver.main()
        self.assertEqual(exit_code, ExitCode.USER_INPUT_ERROR)
        output = mock_stderr.getvalue()
        self.assertIn("'unknown_command_xyz' is not a valid command", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_unknown_command_with_fuzzy_match(self, mock_stderr):
        """Test unknown command with fuzzy matching suggestion"""
        sys.argv = ['geai', 'halp']
        exit_code = self.driver.main()
        self.assertEqual(exit_code, ExitCode.USER_INPUT_ERROR)
        output = mock_stderr.getvalue()
        self.assertIn("'halp' is not a valid command", output)
        self.assertIn("Did you mean", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_help_command_exit_code(self, mock_stdout):
        """Test that help command returns success exit code"""
        sys.argv = ['geai', 'help']
        exit_code = self.driver.main()
        self.assertEqual(exit_code, ExitCode.SUCCESS)

    @patch('sys.stdout', new_callable=StringIO)
    def test_version_command_exit_code(self, mock_stdout):
        """Test that version command returns success exit code"""
        sys.argv = ['geai', 'version']
        exit_code = self.driver.main()
        self.assertEqual(exit_code, ExitCode.SUCCESS)

    @patch('sys.stderr', new_callable=StringIO)
    def test_invalid_option_exit_code(self, mock_stderr):
        """Test that invalid option returns correct exit code"""
        sys.argv = ['geai', 'configure', '--invalid-option-xyz']
        exit_code = self.driver.main()
        self.assertEqual(exit_code, ExitCode.USER_INPUT_ERROR)
        output = mock_stderr.getvalue()
        self.assertIn("'--invalid-option-xyz' is not a valid option", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_error_message_format(self, mock_stderr):
        """Test that error messages follow the standard format"""
        sys.argv = ['geai', 'invalidcmd']
        exit_code = self.driver.main()
        output = mock_stderr.getvalue()
        
        # Check for standard error format
        self.assertIn("ERROR:", output)
        self.assertIn("→", output)
        self.assertIn("Run 'geai help' for usage information", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_available_commands_shown(self, mock_stderr):
        """Test that available commands are shown for unknown command"""
        sys.argv = ['geai', 'xyz123']
        exit_code = self.driver.main()
        output = mock_stderr.getvalue()
        
        # Should show available commands
        self.assertIn("Available commands:", output)
        self.assertIn("help", output)
        self.assertIn("version", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_similar_command_suggestion(self, mock_stderr):
        """Test that similar commands are suggested"""
        sys.argv = ['geai', 'versoin']  # Typo in 'version'
        exit_code = self.driver.main()
        output = mock_stderr.getvalue()
        
        self.assertIn("Did you mean", output)
        self.assertIn("version", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_keyboard_interrupt_exit_code(self, mock_stdout):
        """Test keyboard interrupt handling"""
        sys.argv = ['geai', 'help']
        
        with patch.object(self.driver, 'process_command', side_effect=KeyboardInterrupt):
            exit_code = self.driver.main()
            self.assertEqual(exit_code, ExitCode.KEYBOARD_INTERRUPT)
            output = mock_stdout.getvalue()
            self.assertIn("Operation cancelled", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_unexpected_error_exit_code(self, mock_stderr):
        """Test unexpected error handling"""
        sys.argv = ['geai', 'help']
        
        with patch.object(self.driver, 'process_command', side_effect=RuntimeError("Test error")):
            exit_code = self.driver.main()
            self.assertEqual(exit_code, ExitCode.UNEXPECTED_ERROR)
            output = mock_stderr.getvalue()
            self.assertIn("unexpected error", output)
            self.assertIn("Test error", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_configure_with_typo_in_option(self, mock_stderr):
        """Test configure command with typo in option"""
        sys.argv = ['geai', 'configure', '--kee']  # Typo in '--key'
        exit_code = self.driver.main()
        self.assertEqual(exit_code, ExitCode.USER_INPUT_ERROR)
        output = mock_stderr.getvalue()
        self.assertIn("'--kee' is not a valid option", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_default_to_help_when_no_args(self, mock_stdout):
        """Test that CLI defaults to help when no arguments provided"""
        sys.argv = ['geai']
        exit_code = self.driver.main()
        self.assertEqual(exit_code, ExitCode.SUCCESS)
        output = mock_stdout.getvalue()
        self.assertIn("GEAI CLI", output)

    def test_exit_codes_are_different(self):
        """Test that different error types have different exit codes"""
        exit_codes = [
            ExitCode.SUCCESS,
            ExitCode.USER_INPUT_ERROR,
            ExitCode.MISSING_REQUIREMENT,
            ExitCode.SERVICE_ERROR,
            ExitCode.KEYBOARD_INTERRUPT,
            ExitCode.UNEXPECTED_ERROR,
        ]
        
        # All exit codes should be unique
        self.assertEqual(len(exit_codes), len(set(exit_codes)))


if __name__ == '__main__':
    unittest.main()
