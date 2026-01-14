from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

evaluation_plan_id = "your-evaluation-plan-id"

response = client.list_evaluation_plan_system_metrics(evaluation_plan_id=evaluation_plan_id)

print(f"Plan system metrics: {response}")
