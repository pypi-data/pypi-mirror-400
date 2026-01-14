from json import JSONDecodeError

from pygeai import logger
from pygeai.core.common.exceptions import InvalidAPIResponseException


def parse_json_response(response, operation: str, **context):
    """
    Parse JSON response with standardized error handling.

    :param response: HTTP response object
    :param operation: Description of operation (e.g., "get project API token")
    :param context: Additional context (e.g., api_token_id="123")
    :return: Parsed JSON response
    :raises InvalidAPIResponseException: If JSON parsing fails
    """
    try:
        return response.json()
    except JSONDecodeError as e:
        full_msg = f"Unable to {operation}"
        if context:
            if len(context) == 1:
                # Single context value: append as 'value'
                value = list(context.values())[0]
                full_msg += f" '{value}'"
            else:
                # Multiple context values: format as (key1='value1', key2='value2')
                context_str = ", ".join([f"{k}='{v}'" for k, v in context.items()])
                full_msg += f" ({context_str})"

        logger.error(f"{full_msg}: JSON parsing error (status {response.status_code}): {e}. Response: {response.text}")
        raise InvalidAPIResponseException(f"{full_msg}: {response.text}")
