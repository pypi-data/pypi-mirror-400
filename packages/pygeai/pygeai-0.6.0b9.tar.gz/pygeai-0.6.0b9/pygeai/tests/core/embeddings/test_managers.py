import unittest
from unittest.mock import patch, MagicMock
from pygeai.core.embeddings.managers import EmbeddingsManager
from pygeai.core.embeddings.models import EmbeddingConfiguration
from pygeai.core.embeddings.responses import EmbeddingResponse
from pygeai.core.common.exceptions import APIError


class TestEmbeddingsManager(unittest.TestCase):
    """
    python -m unittest pygeai.tests.core.embeddings.test_managers.TestEmbeddingsManager
    """

    def setUp(self):
        self.manager = EmbeddingsManager()
        self.config = EmbeddingConfiguration(
            inputs=["test input"],
            model="test-model"
        )

    @patch('pygeai.core.embeddings.clients.EmbeddingsClient.generate_embeddings')
    def test_generate_embeddings_success(self, mock_generate):
        mock_generate.return_value = {
            "model": "test-model",
            "object": "list",
            "data": [
                {
                    "index": 0,
                    "embedding": [0.1, 0.2, 0.3],
                    "object": "embedding"
                }
            ],
            "usage": {
                "prompt_tokens": 5,
                "total_tokens": 5,
                "total_cost": 0.0001,
                "currency": "USD",
                "prompt_cost": 0.0001,
                "completion_tokens_details": None,
                "prompt_tokens_details": None
            }
        }

        result = self.manager.generate_embeddings(self.config)

        self.assertIsInstance(result, EmbeddingResponse)
        self.assertEqual(result.model, "test-model")
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].index, 0)
        self.assertEqual(result.usage.prompt_tokens, 5)
        self.assertEqual(result.usage.total_cost, 0.0001)

    @patch('pygeai.core.embeddings.clients.EmbeddingsClient.generate_embeddings')
    def test_generate_embeddings_with_all_config_parameters(self, mock_generate):
        mock_generate.return_value = {
            "model": "test-model",
            "object": "list",
            "data": [{"index": 0, "embedding": [0.1], "object": "embedding"}],
            "usage": {
                "prompt_tokens": 5,
                "total_tokens": 5,
                "total_cost": 0.0001,
                "currency": "USD",
                "prompt_cost": 0.0001,
                "completion_tokens_details": None,
                "prompt_tokens_details": None
            }
        }

        config = EmbeddingConfiguration(
            inputs=["test"],
            model="test-model",
            encoding_format="base64",
            dimensions=512,
            user="user123",
            input_type="query",
            timeout=30,
            cache=True
        )

        result = self.manager.generate_embeddings(config)

        mock_generate.assert_called_once_with(
            input_list=["test"],
            model="test-model",
            encoding_format="base64",
            dimensions=512,
            user="user123",
            input_type="query",
            timeout=30,
            cache=True
        )
        self.assertIsInstance(result, EmbeddingResponse)

    @patch('pygeai.core.embeddings.clients.EmbeddingsClient.generate_embeddings')
    def test_generate_embeddings_with_error(self, mock_generate):
        mock_generate.return_value = {
            "error": {
                "message": "Invalid model",
                "type": "invalid_request_error"
            }
        }

        with self.assertRaises(APIError) as context:
            self.manager.generate_embeddings(self.config)

        self.assertIn("Error received while generating embeddings", str(context.exception))

    @patch('pygeai.core.embeddings.clients.EmbeddingsClient.generate_embeddings')
    def test_generate_embeddings_multiple_inputs(self, mock_generate):
        mock_generate.return_value = {
            "model": "test-model",
            "object": "list",
            "data": [
                {"index": 0, "embedding": [0.1, 0.2], "object": "embedding"},
                {"index": 1, "embedding": [0.3, 0.4], "object": "embedding"}
            ],
            "usage": {
                "prompt_tokens": 10,
                "total_tokens": 10,
                "total_cost": 0.0002,
                "currency": "USD",
                "prompt_cost": 0.0002,
                "completion_tokens_details": None,
                "prompt_tokens_details": None
            }
        }

        config = EmbeddingConfiguration(
            inputs=["input1", "input2"],
            model="test-model"
        )

        result = self.manager.generate_embeddings(config)

        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0].index, 0)
        self.assertEqual(result.data[1].index, 1)

    @patch('pygeai.core.embeddings.clients.EmbeddingsClient.generate_embeddings')
    def test_generate_embeddings_with_token_details(self, mock_generate):
        mock_generate.return_value = {
            "model": "test-model",
            "object": "list",
            "data": [{"index": 0, "embedding": [0.1], "object": "embedding"}],
            "usage": {
                "prompt_tokens": 5,
                "total_tokens": 5,
                "total_cost": 0.0001,
                "currency": "USD",
                "prompt_cost": 0.0001,
                "completion_tokens_details": {
                    "reasoning_tokens": 0,
                    "cached_tokens": 0
                },
                "prompt_tokens_details": {
                    "reasoning_tokens": 0,
                    "cached_tokens": 5
                }
            }
        }

        result = self.manager.generate_embeddings(self.config)

        self.assertIsNotNone(result.usage.completion_tokens_details)
        self.assertIsNotNone(result.usage.prompt_tokens_details)
        self.assertEqual(result.usage.prompt_tokens_details.cached_tokens, 5)


if __name__ == '__main__':
    unittest.main()
