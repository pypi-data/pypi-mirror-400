from pygeai.evaluation.result.clients import EvaluationResultClient

client = EvaluationResultClient()

evaluation_plan_id = "your-evaluation-plan-id"

results = client.list_evaluation_results(evaluation_plan_id=evaluation_plan_id)

print(f"Found {len(results) if isinstance(results, list) else 'N/A'} evaluation results")

for result in results if isinstance(results, list) else []:
    print(f"\nResult ID: {result.get('evaluationResultId')}")
    print(f"  Status: {result.get('evaluationResultStatus')}")
    print(f"  Cost: ${result.get('evaluationResultCost')}")
    print(f"  Duration: {result.get('evaluationResultDuration')}ms")
    print(f"  Start: {result.get('evaluationResultStartDate')}")
    print(f"  End: {result.get('evaluationResultEndDate')}")
