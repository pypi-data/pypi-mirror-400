from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
row_id = "your-row-id-here"
source_id = "your-expected-source-id-here"

response = client.get_expected_source(
    dataset_id=dataset_id,
    dataset_row_id=row_id,
    expected_source_id=source_id
)

print(f"Expected source details: {response}")
