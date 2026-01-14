from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

dataset_id = "your-dataset-id-here"
row_id = "your-row-id-here"

response = client.create_filter_variable(
    dataset_id=dataset_id,
    dataset_row_id=row_id,
    metadata_type="V",
    filter_variable_key="category",
    filter_variable_value="science",
    filter_variable_operator="="
)

print(f"Created filter variable: {response}")
filter_var_id = response.get('dataSetRowFilterVarId')
print(f"Filter Variable ID: {filter_var_id}")
