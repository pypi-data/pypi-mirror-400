from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

evaluation_plan_id = "your-evaluation-plan-id"
system_metric_id = "your-metric-id"

response = client.update_evaluation_plan_system_metric(
    evaluation_plan_id=evaluation_plan_id,
    system_metric_id=system_metric_id,
    system_metric_weight=0.9
)

print(f"Updated system metric: {response}")
