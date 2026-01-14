
from pygeai import logger
from pygeai.core.base.clients import BaseClient
from pygeai.core.common.exceptions import InvalidAPIResponseException
from pygeai.core.llm.endpoints import GET_PROVIDER_LIST_V2, GET_PROVIDER_DATA_V2, GET_PROVIDER_MODELS_V2, \
    GET_MODEL_DATA_V2
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response


class LlmClient(BaseClient):

    def get_provider_list(self) -> dict:
        logger.debug("Obtaining provider list")
        response = self.api_service.get(endpoint=GET_PROVIDER_LIST_V2)
        validate_status_code(response)
        return parse_json_response(response, "obtain provider list")

    def get_provider_data(self, provider_name: str) -> dict:
        endpoint = GET_PROVIDER_DATA_V2.format(providerName=provider_name)

        logger.debug(f"Obtaining provider data for {provider_name}")

        response = self.api_service.get(endpoint=endpoint)
        validate_status_code(response)
        return parse_json_response(response, "obtain provider data", provider_name=provider_name)

    def get_provider_models(self, provider_name: str) -> dict:
        endpoint = GET_PROVIDER_MODELS_V2.format(providerName=provider_name)

        logger.debug(f"Obtaining provider models for {provider_name}")

        response = self.api_service.get(endpoint=endpoint)
        validate_status_code(response)
        return parse_json_response(response, "obtain provider models", provider_name=provider_name)

    def get_model_data(
            self,
            provider_name: str,
            model_name: str = None,
            model_id: str = None
    ) -> dict:
        endpoint = GET_MODEL_DATA_V2.format(
            providerName=provider_name,
            modelNameOrId=model_name or model_id
        )

        logger.debug(f"Obtaining model data for {provider_name}/{model_name or model_id}")

        response = self.api_service.get(endpoint=endpoint)
        model_identifier = model_name or model_id
        validate_status_code(response)
        return parse_json_response(response, f"obtain model data for {provider_name}/{model_identifier}")
