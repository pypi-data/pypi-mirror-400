from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

system_metric_id = "your-metric-id"

response = client.get_system_metric(system_metric_id=system_metric_id)

print(f"System metric: {response}")
