from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

evaluation_plan_id = "your-evaluation-plan-id"

response = client.delete_evaluation_plan(evaluation_plan_id=evaluation_plan_id)

print(f"Deleted evaluation plan: {response}")
