from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
file_path = "path/to/rows.json"

response = client.upload_dataset_rows_file(dataset_id=dataset_id, file_path=file_path)

print(f"Uploaded rows from file: {response}")
