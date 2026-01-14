from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"

row = {
    "dataSetRowInput": "What is AI?",
    "dataSetRowExpectedAnswer": "Artificial Intelligence is the simulation of human intelligence by machines.",
    "dataSetRowContextDocument": "AI enables computers to perform tasks that typically require human intelligence."
}

response = client.create_dataset_row(dataset_id=dataset_id, row=row)

print(f"Created row: {response}")
row_id = response.get('dataSetRowId')
print(f"Row ID: {row_id}")
