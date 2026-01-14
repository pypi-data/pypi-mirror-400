from pygeai import logger
from pygeai.core.common.exceptions import APIResponseError


def validate_status_code(response):
    if response.status_code >= 300:
        logger.error(f"Invalid status code returned from the API endpoint: {response.text}")
        raise APIResponseError(f"API returned an error: {response.text}")


