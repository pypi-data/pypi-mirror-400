import unittest
from unittest.mock import patch, MagicMock
from json import JSONDecodeError

from pygeai.auth.clients import AuthClient
from pygeai.core.common.exceptions import InvalidAPIResponseException, APIResponseError


class TestAuthClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.auth.test_clients.TestAuthClient
    """

    def setUp(self):
        self.client = AuthClient()
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200  # Default to success status

    @patch('pygeai.core.services.rest.ApiService.get')
    def test_get_oauth2_access_token_success(self, mock_get):
        self.mock_response.json.return_value = {"access_token": "token-123", "token_type": "Bearer"}
        mock_get.return_value = self.mock_response
        
        result = self.client.get_oauth2_access_token(
            client_id="client-123",
            username="user@example.com",
            password="password123"
        )
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['params']['client_id'], "client-123")
        self.assertEqual(call_args[1]['params']['username'], "user@example.com")
        self.assertEqual(call_args[1]['params']['password'], "password123")
        self.assertEqual(call_args[1]['params']['scope'], "gam_user_data gam_user_roles")
        self.assertEqual(result, {"access_token": "token-123", "token_type": "Bearer"})

    @patch('pygeai.core.services.rest.ApiService.get')
    def test_get_oauth2_access_token_custom_scope(self, mock_get):
        self.mock_response.json.return_value = {"access_token": "token-123"}
        self.mock_response.status_code = 200
        mock_get.return_value = self.mock_response
        
        result = self.client.get_oauth2_access_token(
            client_id="client-123",
            username="user@example.com",
            password="password123",
            scope="custom_scope"
        )
        
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['params']['scope'], "custom_scope")

    @patch('pygeai.core.services.rest.ApiService.get')
    def test_get_oauth2_access_token_error_status(self, mock_get):
        self.mock_response.status_code = 401
        self.mock_response.text = "Invalid credentials"
        mock_get.return_value = self.mock_response
        
        with self.assertRaises(APIResponseError) as context:
            self.client.get_oauth2_access_token(
                client_id="client-123",
                username="user@example.com",
                password="wrong"
            )
        self.assertIn("API returned an error", str(context.exception))  # "API returned an error", str(context.exception))

    @patch.object(AuthClient, 'api_service', create=True)
    def test_get_user_profile_information_success(self, mock_api_service):
        self.mock_response.json.return_value = {
            "user_id": "user-123",
            "email": "user@example.com",
            "name": "Test User"
        }
        self.mock_response.status_code = 200
        mock_api_service.get.return_value = self.mock_response
        mock_api_service.token = None
        
        client = AuthClient()
        client.api_service = mock_api_service
        result = client.get_user_profile_information("access-token-123")
        
        mock_api_service.get.assert_called_once()
        self.assertEqual(result, {
            "user_id": "user-123",
            "email": "user@example.com",
            "name": "Test User"
        })

    @patch.object(AuthClient, 'api_service', create=True)
    def test_get_user_profile_information_json_decode_error(self, mock_api_service):
        self.mock_response.json.side_effect = JSONDecodeError("error", "doc", 0)
        self.mock_response.status_code = 401
        self.mock_response.text = "Invalid token"
        mock_api_service.get.return_value = self.mock_response
        mock_api_service.token = None
        
        client = AuthClient()
        client.api_service = mock_api_service
        
        with self.assertRaises(APIResponseError) as context:
            client.get_user_profile_information("invalid-token")
        self.assertIn("API returned an error", str(context.exception))  # "API returned an error", str(context.exception))

    @patch('pygeai.core.services.rest.ApiService.post')
    def test_create_project_api_token_success(self, mock_post):
        self.mock_response.json.return_value = {
            "id": "test_token_id",
            "name": "TestToken",
            "description": "Test Token",
            "status": "Active",
            "scope": "Pia.Data.Organization",
            "organization": "org-123",
            "project": "project-123",
            "messages": [
                {
                    "id": 0,
                    "description": "Token created successfully",
                    "type": "Success"
                }
            ],
            "errors": []
        }
        self.mock_response.status_code = 200
        mock_post.return_value = self.mock_response
        
        result = self.client.create_project_api_token(
            project_id="project-123",
            name="TestToken",
            description="Test Token"
        )
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['name'], "TestToken")
        self.assertEqual(call_args[1]['data']['description'], "Test Token")
        self.assertEqual(call_args[1]['headers']['project-id'], "project-123")
        self.assertEqual(result['name'], "TestToken")
        self.assertEqual(result['id'], "test_token_id")

    @patch('pygeai.core.services.rest.ApiService.post')
    def test_create_project_api_token_without_description(self, mock_post):
        self.mock_response.json.return_value = {
            "id": "test_token_id",
            "name": "TestToken",
            "status": "Active"
        }
        self.mock_response.status_code = 200
        mock_post.return_value = self.mock_response
        
        result = self.client.create_project_api_token(
            project_id="project-123",
            name="TestToken"
        )
        
        call_args = mock_post.call_args
        self.assertNotIn('description', call_args[1]['data'])

    @patch('pygeai.core.services.rest.ApiService.post')
    def test_create_project_api_token_json_decode_error(self, mock_post):
        self.mock_response.json.side_effect = JSONDecodeError("error", "doc", 0)
        self.mock_response.status_code = 400
        self.mock_response.text = "Bad request"
        mock_post.return_value = self.mock_response
        
        with self.assertRaises(APIResponseError) as context:
            self.client.create_project_api_token(
                project_id="project-123",
                name="TestToken"
            )
        self.assertIn("API returned an error", str(context.exception))  # "API returned an error", str(context.exception))

    @patch('pygeai.core.services.rest.ApiService.delete')
    def test_delete_project_api_token_success(self, mock_delete):
        self.mock_response.json.return_value = {}
        self.mock_response.status_code = 200
        mock_delete.return_value = self.mock_response
        
        result = self.client.delete_project_api_token(api_token_id="token-123")
        
        mock_delete.assert_called_once()
        call_args = mock_delete.call_args
        self.assertIn("token-123", call_args[1]['endpoint'])
        self.assertEqual(result, {})

    @patch('pygeai.core.services.rest.ApiService.delete')
    def test_delete_project_api_token_json_decode_error(self, mock_delete):
        self.mock_response.json.side_effect = JSONDecodeError("error", "doc", 0)
        self.mock_response.status_code = 404
        self.mock_response.text = "Not found"
        mock_delete.return_value = self.mock_response
        
        with self.assertRaises(APIResponseError) as context:
            self.client.delete_project_api_token(api_token_id="invalid-token")
        self.assertIn("API returned an error", str(context.exception))  # "API returned an error", str(context.exception))

    @patch('pygeai.core.services.rest.ApiService.put')
    def test_update_project_api_token_success(self, mock_put):
        self.mock_response.json.return_value = [
            {
                "description": "Token updated successfully",
                "type": "Success"
            }
        ]
        self.mock_response.status_code = 200
        mock_put.return_value = self.mock_response
        
        result = self.client.update_project_api_token(
            api_token_id="token-123",
            description="Updated description",
            status="blocked"
        )
        
        mock_put.assert_called_once()
        call_args = mock_put.call_args
        self.assertEqual(call_args[1]['data']['description'], "Updated description")
        self.assertEqual(call_args[1]['data']['status'], "blocked")
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['type'], "Success")

    @patch('pygeai.core.services.rest.ApiService.put')
    def test_update_project_api_token_only_description(self, mock_put):
        self.mock_response.json.return_value = [
            {
                "description": "Token updated successfully",
                "type": "Success"
            }
        ]
        self.mock_response.status_code = 200
        mock_put.return_value = self.mock_response
        
        result = self.client.update_project_api_token(
            api_token_id="token-123",
            description="New description"
        )
        
        call_args = mock_put.call_args
        self.assertEqual(call_args[1]['data']['description'], "New description")
        self.assertNotIn('status', call_args[1]['data'])

    @patch('pygeai.core.services.rest.ApiService.put')
    def test_update_project_api_token_json_decode_error(self, mock_put):
        self.mock_response.json.side_effect = JSONDecodeError("error", "doc", 0)
        self.mock_response.status_code = 400
        self.mock_response.text = "Bad request"
        mock_put.return_value = self.mock_response
        
        with self.assertRaises(APIResponseError) as context:
            self.client.update_project_api_token(
                api_token_id="token-123",
                description="New description"
            )
        self.assertIn("API returned an error", str(context.exception))  # "API returned an error", str(context.exception))

    @patch('pygeai.core.services.rest.ApiService.get')
    def test_get_project_api_token_success(self, mock_get):
        self.mock_response.json.return_value = {
            "id": "token-123",
            "name": "Default",
            "description": "Default token",
            "status": "Active",
            "scope": "Pia.Data.Organization",
            "timestamp": "2024-07-22T18:37:32.341"
        }
        self.mock_response.status_code = 200
        mock_get.return_value = self.mock_response
        
        result = self.client.get_project_api_token(api_token_id="token-123")
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("token-123", call_args[1]['endpoint'])
        self.assertEqual(result['id'], "token-123")
        self.assertEqual(result['status'], "Active")

    @patch('pygeai.core.services.rest.ApiService.get')
    def test_get_project_api_token_json_decode_error(self, mock_get):
        self.mock_response.json.side_effect = JSONDecodeError("error", "doc", 0)
        self.mock_response.status_code = 404
        self.mock_response.text = "Not found"
        mock_get.return_value = self.mock_response
        
        with self.assertRaises(APIResponseError) as context:
            self.client.get_project_api_token(api_token_id="invalid-token")
        self.assertIn("API returned an error", str(context.exception))  # "API returned an error", str(context.exception))


if __name__ == '__main__':
    unittest.main()
