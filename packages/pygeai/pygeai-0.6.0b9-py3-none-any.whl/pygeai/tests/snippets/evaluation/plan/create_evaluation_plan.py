from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

response = client.create_evaluation_plan(
    name="My Evaluation Plan",
    type="TextPromptAssistant",
    assistant_id="your-assistant-id",
    assistant_name="My Assistant",
    assistant_revision="1.0",
    dataset_id="your-dataset-id",
    system_metrics=[
        {
            "systemMetricId": "metric-1",
            "systemMetricWeight": 0.6
        },
        {
            "systemMetricId": "metric-2",
            "systemMetricWeight": 0.4
        }
    ]
)

print(f"Created evaluation plan: {response}")
