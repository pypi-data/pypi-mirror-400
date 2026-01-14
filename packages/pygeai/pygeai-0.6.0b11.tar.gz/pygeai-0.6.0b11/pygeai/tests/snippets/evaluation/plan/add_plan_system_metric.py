from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

evaluation_plan_id = "your-evaluation-plan-id"

response = client.add_evaluation_plan_system_metric(
    evaluation_plan_id=evaluation_plan_id,
    system_metric_id="metric-id",
    system_metric_weight=0.5
)

print(f"Added system metric: {response}")
