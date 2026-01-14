from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

response = client.list_evaluation_plans()

print(f"Evaluation plans: {response}")
