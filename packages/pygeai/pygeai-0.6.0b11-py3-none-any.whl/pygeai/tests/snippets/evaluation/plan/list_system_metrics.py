from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

response = client.list_system_metrics()

print(f"Available system metrics: {response}")
