from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"

response = client.update_dataset(
    dataset_id=dataset_id,
    dataset_name="Updated Dataset Name",
    dataset_description="Updated description",
    dataset_type="E",
    dataset_active=False
)

print(f"Updated dataset: {response}")
