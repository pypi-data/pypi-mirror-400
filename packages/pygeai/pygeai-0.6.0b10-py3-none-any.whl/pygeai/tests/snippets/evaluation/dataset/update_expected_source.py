from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
row_id = "your-row-id-here"
source_id = "your-expected-source-id-here"

response = client.update_expected_source(
    dataset_id=dataset_id,
    dataset_row_id=row_id,
    expected_source_id=source_id,
    expected_source_name="Updated Documentation",
    expected_source_value="Updated content from the source...",
    expected_source_extension="txt"
)

print(f"Updated expected source: {response}")
