import json

from pygeai.evaluation.clients import EvaluationClient
from pygeai.evaluation.result.endpoints import LIST_EVALUATION_RESULTS, GET_EVALUATION_RESULT
from pygeai.core.utils.validators import validate_status_code
from pygeai.core.utils.parsers import parse_json_response


class EvaluationResultClient(EvaluationClient):
    """
    Client for interacting with the Evaluation Result API.
    
    This API is read-only and retrieves results from executed evaluation plans.
    
    .. warning::
        The API documentation at https://docs.globant.ai/en/wiki?856,Evaluation+Result+API
        contains several typos in field names. The actual API responses use these typo'd names:
        
        - evaluationResultAssitantRevision (missing 's' in Assistant)
        - evaluationResultChunckCount (should be Chunk, not Chunck)
        - evaluationResultChunckSize (should be Chunk, not Chunck)
        - evaluationResultaMaxTokens (lowercase 'a' should be uppercase 'M', no 'a')
        
        Our implementation returns these fields as-is from the API.
    """

    def list_evaluation_results(self, evaluation_plan_id: str) -> dict:
        """
        Retrieves a list of evaluation results for a given evaluation plan ID.

        :param evaluation_plan_id: str - The ID of the evaluation plan.

        :return: dict - API response containing a list of evaluation results.
        
        .. note::
            Response contains evaluation result objects with fields including:
            dataSetId, evaluationPlanId, evaluationResultId, evaluationResultStatus,
            evaluationResultCost, evaluationResultDuration, and others.
            
            See class documentation for field name typos in the API.
        """
        endpoint = LIST_EVALUATION_RESULTS.format(evaluationPlanId=evaluation_plan_id)
        response = self.api_service.get(
            endpoint=endpoint
        )
        validate_status_code(response)
        return parse_json_response(response, "evaluation plan operation")

    def get_evaluation_result(self, evaluation_result_id: str) -> dict:
        """
        Retrieves a specific evaluation result by its ID.

        :param evaluation_result_id: str - The ID of the evaluation result.

        :return: dict - The evaluation result metadata as a dictionary, including row-level data.
        
        .. note::
            Response includes all fields from list_evaluation_results plus a 'rows' array
            containing detailed row-level evaluation data with fields like:
            dataSetRowId, evaluationResultRowStatus, evaluationResultRowOutput,
            evaluationResultRowCost, etc.
            
            See class documentation for field name typos in the API.
        """
        endpoint = GET_EVALUATION_RESULT.format(evaluationResultId=evaluation_result_id)
        response = self.api_service.get(
            endpoint=endpoint
        )
        validate_status_code(response)
        return parse_json_response(response, "evaluation plan operation")
