from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

evaluation_plan_id = "your-evaluation-plan-id"

response = client.update_evaluation_plan(
    evaluation_plan_id=evaluation_plan_id,
    name="Updated Plan Name",
    system_metrics=[
        {
            "systemMetricId": "metric-1",
            "systemMetricWeight": 0.8
        },
        {
            "systemMetricId": "metric-2",
            "systemMetricWeight": 0.2
        }
    ]
)

print(f"Updated evaluation plan: {response}")
