from typing import Any, Union

from pygeai import logger
from pygeai.core.base.clients import BaseClient
from pygeai.core.common.exceptions import InvalidAPIResponseException
from pygeai.core.feedback.endpoints import SEND_FEEDBACK_V1
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response


class FeedbackClient(BaseClient):

    def send_feedback(
            self,
            request_id: str,
            origin: str = "user-feedback",
            answer_score: int = 1,
            comments: str = None
    ) -> dict:
        """
        Sends feedback for an assistant's response.

        This method submits user feedback to the Feedback API, associating it with a specific request.
        The feedback includes an origin identifier, a score indicating the response quality, and an optional comment.

        :param request_id: str - The request associated with a user's execution.
        :param origin: str - The origin of the feedback. Should be set to "user-feedback".
        :param answer_score: int - The score for the response.
           - 1: Good
           - 2: Bad
        :param comments: str, optional - Additional feedback comments. Defaults to None.
        :return: dict - The parsed JSON response from the API. The expected response is an empty JSON object ({}).
        """
        data = {
            "origin": origin,
            "answerScore": answer_score,
        }
        if comments:
            data["comments"] = comments

        logger.debug(f"Providing feedback with data: {data}")

        endpoint = SEND_FEEDBACK_V1.format(requestId=request_id)
        response = self.api_service.post(
            endpoint=endpoint,
            data=data
        )
        validate_status_code(response)
        return parse_json_response(response, "send feedback. JSON parsing error")

