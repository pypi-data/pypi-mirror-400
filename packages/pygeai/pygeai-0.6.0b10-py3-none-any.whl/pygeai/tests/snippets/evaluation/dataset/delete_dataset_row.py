from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
row_id = "your-row-id-here"

response = client.delete_dataset_row(dataset_id=dataset_id, dataset_row_id=row_id)

print(f"Deleted row: {response}")
