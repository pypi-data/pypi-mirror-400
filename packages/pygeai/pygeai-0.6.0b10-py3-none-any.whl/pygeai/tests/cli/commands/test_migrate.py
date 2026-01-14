import unittest
from unittest.mock import patch, Mock
from pygeai.cli.commands.migrate import clone_project, show_help, migrate_commands


class TestMigrateCommands(unittest.TestCase):

    def mock_option(self, name, value=None):
        option = Mock()
        option.name = name
        return (option, value)

    def test_show_help(self):
        show_help()

    @patch('pygeai.auth.clients.AuthClient')
    @patch('pygeai.cli.commands.migrate.Console.write_stdout')
    @patch('pygeai.cli.commands.migrate.MigrationTool')
    @patch('pygeai.cli.commands.migrate.MigrationOrchestrator')
    @patch('pygeai.cli.commands.migrate.RAGAssistantClient')
    @patch('pygeai.cli.commands.migrate.FileManager')
    @patch('pygeai.cli.commands.migrate.AILabManager')
    @patch("pygeai.admin.clients.AdminClient.validate_api_token", return_value={"projectId": "test_project"})
    def test_clone_project_with_all_flag(self, mock_base_client, mock_lab_mgr, mock_file_mgr, mock_rag_client, mock_orchestrator, mock_migration_tool, mock_stdout, mock_auth_client):
        mock_lab_instance = Mock()
        mock_lab_mgr.return_value = mock_lab_instance
        
        mock_lab_instance.get_agent_list.return_value = Mock(agents=[Mock(id="agent1")])
        mock_lab_instance.list_tools.return_value = Mock(tools=[Mock(id="tool1")])
        mock_lab_instance.list_processes.return_value = Mock(processes=[Mock(id="proc1")])
        mock_lab_instance.list_tasks.return_value = Mock(tasks=[Mock(id="task1")])
        
        mock_rag_instance = Mock()
        mock_rag_client.return_value = mock_rag_instance
        mock_rag_instance.get_assistants_from_project.return_value = {
            "assistants": [
                {
                    "name": "asst1",
                    "searchOptions": {},
                    "indexOptions": {},
                    "welcomeData": None,
                    "llmSettings": None
                }
            ]
        }
        
        mock_file_instance = Mock()
        mock_file_mgr.return_value = mock_file_instance
        mock_file_instance.get_file_list.return_value = Mock(files=[Mock(id="file1")])
        
        mock_migration_tool_instance = Mock()
        mock_migration_tool.return_value = mock_migration_tool_instance
        mock_migration_tool_instance.run_migration.return_value = "proj456"
        
        mock_auth_instance = Mock()
        mock_auth_client.return_value = mock_auth_instance
        mock_auth_instance.create_project_api_token.return_value = {"id": "new_project_api_key", "name": "Migration API Key"}
        
        mock_orch_instance = Mock()
        mock_orchestrator.return_value = mock_orch_instance
        mock_orch_instance.execute.return_value = {"completed": 1, "total": 1, "failed": 0}

        option_list = [
            self.mock_option("from_api_key", "from_key"),
            self.mock_option("from_organization_api_key", "from_org_key"),
            self.mock_option("from_project_id", "proj123"),
            self.mock_option("from_instance", "from_instance"),
            self.mock_option("from_organization_id", "org123"),
            self.mock_option("to_organization_api_key", "to_org_key"),
            self.mock_option("to_project_name", "new_project"),
            self.mock_option("to_organization_id", "org456"),
            self.mock_option("admin_email", "admin@example.com"),
            self.mock_option("all", True)
        ]

        clone_project(option_list)

        mock_migration_tool_instance.run_migration.assert_called_once()
        mock_auth_instance.create_project_api_token.assert_called_once()
        mock_lab_instance.get_agent_list.assert_called_once()
        mock_lab_instance.list_tools.assert_called_once()
        mock_lab_instance.list_processes.assert_called_once()
        mock_lab_instance.list_tasks.assert_called_once()
        mock_rag_instance.get_assistants_from_project.assert_called_once()
        mock_file_instance.get_file_list.assert_called_once()
        mock_orch_instance.execute.assert_called_once()

    @patch('pygeai.cli.commands.migrate.Console.write_stdout')
    @patch('pygeai.cli.commands.migrate.MigrationOrchestrator')
    @patch('pygeai.cli.commands.migrate.AILabManager')
    @patch("pygeai.admin.clients.AdminClient.validate_api_token", return_value={"projectId": "test_project"})
    def test_clone_project_without_project_creation_no_org_keys_needed(self, mock_base_client, mock_lab_mgr, 
                                                                         mock_orchestrator, mock_stdout):
        """Test that migration to existing project works without org keys but requires to_api_key"""
        mock_lab_instance = Mock()
        mock_lab_mgr.return_value = mock_lab_instance
        
        mock_lab_instance.get_agent_list.return_value = Mock(agents=[Mock(id="agent1")])
        
        mock_orch_instance = Mock()
        mock_orchestrator.return_value = mock_orch_instance
        mock_orch_instance.execute.return_value = {"completed": 1, "total": 1, "failed": 0}

        option_list = [
            self.mock_option("from_api_key", "from_key"),
            self.mock_option("from_project_id", "proj123"),
            self.mock_option("from_instance", "from_instance"),
            self.mock_option("to_project_id", "proj456"),
            self.mock_option("to_api_key", "to_key"),
            self.mock_option("agents", "all")
        ]

        clone_project(option_list)

        mock_lab_instance.get_agent_list.assert_called_once()
        mock_orch_instance.execute.assert_called_once()

    def test_clone_project_missing_required_params(self):
        from pygeai.core.common.exceptions import MissingRequirementException
        
        option_list = [
            self.mock_option("from_api_key", "from_key"),
        ]

        with self.assertRaises(MissingRequirementException):
            clone_project(option_list)

    def test_clone_project_missing_org_key_when_creating_project(self):
        from pygeai.core.common.exceptions import MissingRequirementException
        
        option_list = [
            self.mock_option("from_api_key", "from_key"),
            self.mock_option("from_project_id", "proj123"),
            self.mock_option("from_instance", "from_instance"),
            self.mock_option("to_project_name", "new_project"),
            self.mock_option("admin_email", "admin@example.com"),
            self.mock_option("agents", "all")
        ]

        with self.assertRaises(MissingRequirementException) as cm:
            clone_project(option_list)
        
        self.assertIn("organization scope API key", str(cm.exception))

    def test_clone_project_missing_to_api_key_when_using_existing_project(self):
        from pygeai.core.common.exceptions import MissingRequirementException
        
        option_list = [
            self.mock_option("from_api_key", "from_key"),
            self.mock_option("from_project_id", "proj123"),
            self.mock_option("from_instance", "from_instance"),
            self.mock_option("to_project_id", "proj456"),
            self.mock_option("agents", "all")
        ]

        with self.assertRaises(MissingRequirementException) as cm:
            clone_project(option_list)
        
        self.assertIn("Destination project API key", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
