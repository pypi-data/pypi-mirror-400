from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
row_id = "your-row-id-here"

updated_row = {
    "dataSetRowInput": "Updated question: What is Machine Learning?",
    "dataSetRowExpectedAnswer": "Updated answer: ML is a subset of AI",
    "dataSetRowContextDocument": "Updated context about ML"
}

response = client.update_dataset_row(
    dataset_id=dataset_id,
    dataset_row_id=row_id,
    row=updated_row
)

print(f"Updated row: {response}")
