from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"

response = client.list_dataset_rows(dataset_id=dataset_id)

print(f"Dataset rows: {response}")
