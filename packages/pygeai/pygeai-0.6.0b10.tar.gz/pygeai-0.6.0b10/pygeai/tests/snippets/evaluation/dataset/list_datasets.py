from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

response = client.list_datasets()
print(f"Datasets: {response}")
