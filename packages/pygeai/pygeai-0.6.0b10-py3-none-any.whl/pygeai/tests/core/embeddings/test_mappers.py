import unittest
from pygeai.core.embeddings.mappers import EmbeddingsResponseMapper
from pygeai.core.embeddings.responses import EmbeddingResponse, EmbeddingData, UsageInfo, TokenDetails


class TestEmbeddingsResponseMapper(unittest.TestCase):
    """
    python -m unittest pygeai.tests.core.embeddings.test_mappers.TestEmbeddingsResponseMapper
    """

    def test_map_to_embedding_response_basic(self):
        data = {
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

        result = EmbeddingsResponseMapper.map_to_embedding_response(data)

        self.assertIsInstance(result, EmbeddingResponse)
        self.assertEqual(result.model, "test-model")
        self.assertEqual(result.object, "list")
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].index, 0)
        self.assertEqual(result.data[0].embedding, [0.1, 0.2, 0.3])

    def test_map_to_embedding_data_list(self):
        data = [
            {"index": 0, "embedding": [0.1, 0.2], "object": "embedding"},
            {"index": 1, "embedding": [0.3, 0.4], "object": "embedding"}
        ]

        result = EmbeddingsResponseMapper.map_to_embedding_data_list(data)

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], EmbeddingData)
        self.assertEqual(result[0].index, 0)
        self.assertEqual(result[1].index, 1)

    def test_map_to_embedding_data_with_base64(self):
        data = [
            {"index": 0, "embedding": "base64string==", "object": "embedding"}
        ]

        result = EmbeddingsResponseMapper.map_to_embedding_data_list(data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].embedding, "base64string==")
        self.assertIsInstance(result[0].embedding, str)

    def test_map_to_usage_info_basic(self):
        data = {
            "prompt_tokens": 10,
            "total_tokens": 10,
            "total_cost": 0.0002,
            "currency": "USD",
            "prompt_cost": 0.0002,
            "completion_tokens_details": None,
            "prompt_tokens_details": None
        }

        result = EmbeddingsResponseMapper.map_to_usage_info(data)

        self.assertIsInstance(result, UsageInfo)
        self.assertEqual(result.prompt_tokens, 10)
        self.assertEqual(result.total_tokens, 10)
        self.assertEqual(result.total_cost, 0.0002)
        self.assertEqual(result.currency, "USD")
        self.assertEqual(result.prompt_cost, 0.0002)
        self.assertIsNone(result.completion_tokens_details)
        self.assertIsNone(result.prompt_tokens_details)

    def test_map_to_usage_info_with_token_details(self):
        data = {
            "prompt_tokens": 10,
            "total_tokens": 10,
            "total_cost": 0.0002,
            "currency": "USD",
            "prompt_cost": 0.0002,
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "cached_tokens": 0
            },
            "prompt_tokens_details": {
                "reasoning_tokens": 0,
                "cached_tokens": 5
            }
        }

        result = EmbeddingsResponseMapper.map_to_usage_info(data)

        self.assertIsNotNone(result.completion_tokens_details)
        self.assertIsNotNone(result.prompt_tokens_details)
        self.assertIsInstance(result.completion_tokens_details, TokenDetails)
        self.assertIsInstance(result.prompt_tokens_details, TokenDetails)
        self.assertEqual(result.prompt_tokens_details.cached_tokens, 5)

    def test_parse_token_details_with_none(self):
        result = EmbeddingsResponseMapper._parse_token_details(None)
        self.assertIsNone(result)

    def test_parse_token_details_with_data(self):
        data = {
            "reasoning_tokens": 10,
            "cached_tokens": 5
        }

        result = EmbeddingsResponseMapper._parse_token_details(data)

        self.assertIsInstance(result, TokenDetails)
        self.assertEqual(result.reasoning_tokens, 10)
        self.assertEqual(result.cached_tokens, 5)

    def test_map_to_embedding_response_with_missing_fields(self):
        data = {
            "model": "test-model"
        }

        result = EmbeddingsResponseMapper.map_to_embedding_response(data)

        self.assertEqual(result.model, "test-model")
        self.assertEqual(result.object, "")
        self.assertEqual(len(result.data), 0)


if __name__ == '__main__':
    unittest.main()
