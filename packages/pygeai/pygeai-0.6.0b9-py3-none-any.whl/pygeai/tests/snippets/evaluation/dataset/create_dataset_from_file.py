from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

file_path = "path/to/dataset.json"

response = client.create_dataset_from_file(file_path=file_path)

print(f"Created dataset from file: {response}")
dataset_id = response.get('dataSetId')
print(f"Dataset ID: {dataset_id}")
