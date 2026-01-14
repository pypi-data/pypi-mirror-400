from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"

response = client.get_dataset(dataset_id=dataset_id)

print(f"Dataset details: {response}")
