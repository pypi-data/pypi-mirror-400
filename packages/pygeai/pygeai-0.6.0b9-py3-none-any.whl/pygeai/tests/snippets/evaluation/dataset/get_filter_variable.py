from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
row_id = "your-row-id-here"
filter_var_id = "your-filter-variable-id-here"

response = client.get_filter_variable(
    dataset_id=dataset_id,
    dataset_row_id=row_id,
    filter_variable_id=filter_var_id
)

print(f"Filter variable details: {response}")
