from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

client = EvaluationDatasetClient()

response = client.create_dataset(
    dataset_name="My Test Dataset",
    dataset_description="A dataset for testing purposes",
    dataset_type="T",
    dataset_active=True,
    rows=[
        {
            "dataSetRowInput": "What is the capital of France?",
            "dataSetRowExpectedAnswer": "Paris",
            "dataSetRowContextDocument": "France is a country in Europe."
        },
        {
            "dataSetRowInput": "What is 2+2?",
            "dataSetRowExpectedAnswer": "4",
            "dataSetRowContextDocument": ""
        }
    ]
)

print(f"Created dataset: {response}")
dataset_id = response.get('dataSetId')
print(f"Dataset ID: {dataset_id}")
