from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
row_id = "your-row-id-here"

response = client.create_expected_source(
    dataset_id=dataset_id,
    dataset_row_id=row_id,
    expected_source_name="Documentation PDF",
    expected_source_value="This is the content from the source document...",
    expected_source_extension="pdf"
)

print(f"Created expected source: {response}")
source_id = response.get('dataSetExpectedSourceId')
print(f"Expected Source ID: {source_id}")
