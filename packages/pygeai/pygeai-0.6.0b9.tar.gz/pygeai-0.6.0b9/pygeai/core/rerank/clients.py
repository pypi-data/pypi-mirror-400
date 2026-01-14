from typing import Any, Union

from pygeai import logger
from pygeai.core.base.clients import BaseClient
from pygeai.core.common.exceptions import InvalidAPIResponseException
from pygeai.core.rerank.endpoints import RERANK_V1
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response


class RerankClient(BaseClient):

    def rerank_chunks(
            self,
            query: str,
            model: str,
            documents: list[str],
            top_n: int = 3
    ) -> dict:
        data = {
            "query": query,
            "model": model,
            "documents": documents,
            "top_n": top_n
        }

        logger.debug(f"Generating rerank with data: {data}")

        response = self.api_service.post(
            endpoint=RERANK_V1,
            data=data
        )
        validate_status_code(response)
        return parse_json_response(response, "rerank chunks for query with model", query=query, model=model)

