from pygeai.evaluation.plan.clients import EvaluationPlanClient

client = EvaluationPlanClient()

response = client.create_evaluation_plan(
    name="RAG Assistant Evaluation",
    type="RAG Assistant",
    profile_name="My RAG Profile",
    dataset_id="your-dataset-id",
    system_metrics=[
        {
            "systemMetricId": "accuracy",
            "systemMetricWeight": 0.7
        },
        {
            "systemMetricId": "fluency",
            "systemMetricWeight": 0.3
        }
    ]
)

print(f"Created RAG evaluation plan: {response}")
