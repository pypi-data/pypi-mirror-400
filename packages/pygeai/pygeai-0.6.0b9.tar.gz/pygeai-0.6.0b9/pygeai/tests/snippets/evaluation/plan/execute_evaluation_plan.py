from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

evaluation_plan_id = "your-evaluation-plan-id"

response = client.execute_evaluation_plan(evaluation_plan_id=evaluation_plan_id)

print(f"Execution started: {response}")
print(f"Execution ID: {response.get('executionId')}")
print(f"Status: {response.get('status')}")
