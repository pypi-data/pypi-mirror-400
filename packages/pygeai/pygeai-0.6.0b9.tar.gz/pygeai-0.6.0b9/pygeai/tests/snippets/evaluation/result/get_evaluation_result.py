from pygeai.evaluation.result.clients import EvaluationResultClient

client = EvaluationResultClient()

evaluation_result_id = "your-evaluation-result-id"

result = client.get_evaluation_result(evaluation_result_id=evaluation_result_id)

print(f"Evaluation Result: {result.get('evaluationResultId')}")
print(f"Status: {result.get('evaluationResultStatus')}")
print(f"Plan ID: {result.get('evaluationPlanId')}")
print(f"Dataset ID: {result.get('dataSetId')}")
print(f"Cost: ${result.get('evaluationResultCost')}")
print(f"Duration: {result.get('evaluationResultDuration')}ms")
print(f"Model: {result.get('evaluationResultModelName')}")
print(f"Provider: {result.get('evaluationResultProviderName')}")

# Row-level details
rows = result.get('rows', [])
print(f"\nRow-level results: {len(rows)} rows")

for row in rows:
    print(f"\n  Row ID: {row.get('dataSetRowId')}")
    print(f"    Status: {row.get('evaluationResultRowStatus')}")
    print(f"    Cost: ${row.get('evaluationResultRowCost')}")
    print(f"    Output: {row.get('evaluationResultRowOutput')[:100]}...")
