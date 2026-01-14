"""
Complete Dataset API Workflow Example

This example demonstrates a full workflow using the Dataset API:
1. Create a dataset
2. Add rows
3. Add expected sources
4. Add filter variables
5. Query and update
6. Cleanup

NOTE: API documentation at https://docs.globant.ai/en/wiki?839,DataSet+API contains a typo.
The field 'dataSetExpectedSourceExtension' is spelled correctly in this code.
"""

from pygeai.evaluation.dataset.clients import EvaluationDatasetClient


def main():
    # Initialize client
    client = EvaluationDatasetClient()
    
    print("="*60)
    print("Dataset API Complete Workflow Example")
    print("="*60)
    
    # Step 1: Create a dataset
    print("\n[1/7] Creating dataset...")
    dataset = client.create_dataset(
        dataset_name="AI Knowledge Base - Example",
        dataset_description="A sample dataset for AI-related questions",
        dataset_type="T",
        dataset_active=True,
        rows=[]
    )
    dataset_id = dataset.get('dataSetId')
    print(f"✓ Created dataset: {dataset_id}")
    
    # Step 2: Add rows to the dataset
    print("\n[2/7] Adding rows...")
    row1 = client.create_dataset_row(
        dataset_id=dataset_id,
        row={
            "dataSetRowInput": "What is Machine Learning?",
            "dataSetRowExpectedAnswer": "Machine Learning is a subset of AI that enables systems to learn from data.",
            "dataSetRowContextDocument": "ML is a fundamental concept in artificial intelligence."
        }
    )
    row1_id = row1.get('dataSetRowId')
    print(f"✓ Created row 1: {row1_id}")
    
    row2 = client.create_dataset_row(
        dataset_id=dataset_id,
        row={
            "dataSetRowInput": "What is Deep Learning?",
            "dataSetRowExpectedAnswer": "Deep Learning is a subset of ML using neural networks with multiple layers.",
            "dataSetRowContextDocument": "DL has revolutionized AI in recent years."
        }
    )
    row2_id = row2.get('dataSetRowId')
    print(f"✓ Created row 2: {row2_id}")
    
    # Step 3: Add expected sources to row 1
    print("\n[3/7] Adding expected sources to row 1...")
    source1 = client.create_expected_source(
        dataset_id=dataset_id,
        dataset_row_id=row1_id,
        expected_source_name="Introduction to Machine Learning",
        expected_source_value="Machine Learning is a method of data analysis that automates analytical model building.",
        expected_source_extension="pdf"
    )
    source1_id = source1.get('dataSetExpectedSourceId')
    print(f"✓ Created expected source: {source1_id}")
    
    # Step 4: Add filter variables to row 1
    print("\n[4/7] Adding filter variables to row 1...")
    filter1 = client.create_filter_variable(
        dataset_id=dataset_id,
        dataset_row_id=row1_id,
        metadata_type="V",
        filter_variable_key="category",
        filter_variable_value="machine-learning",
        filter_variable_operator="="
    )
    filter1_id = filter1.get('dataSetRowFilterVarId')
    print(f"✓ Created filter variable: {filter1_id}")
    
    filter2 = client.create_filter_variable(
        dataset_id=dataset_id,
        dataset_row_id=row1_id,
        metadata_type="V",
        filter_variable_key="difficulty",
        filter_variable_value="beginner",
        filter_variable_operator="="
    )
    filter2_id = filter2.get('dataSetRowFilterVarId')
    print(f"✓ Created filter variable: {filter2_id}")
    
    # Step 5: Query the dataset
    print("\n[5/7] Querying dataset...")
    
    # Get full dataset
    full_dataset = client.get_dataset(dataset_id=dataset_id)
    print(f"✓ Dataset has {len(full_dataset.get('rows', []))} rows")
    
    # List all rows
    all_rows = client.list_dataset_rows(dataset_id=dataset_id)
    print(f"✓ Retrieved {len(all_rows) if isinstance(all_rows, list) else 'N/A'} rows")
    
    # Get specific row with all details
    row1_details = client.get_dataset_row(dataset_id=dataset_id, dataset_row_id=row1_id)
    print(f"✓ Row 1 has {len(row1_details.get('expectedSources', []))} expected sources")
    print(f"✓ Row 1 has {len(row1_details.get('filterVariables', []))} filter variables")
    
    # Step 6: Update operations
    print("\n[6/7] Updating resources...")
    
    # Update the dataset description
    updated_dataset = client.update_dataset(
        dataset_id=dataset_id,
        dataset_name="AI Knowledge Base - Updated",
        dataset_description="Updated description for AI dataset",
        dataset_type="T",
        dataset_active=True
    )
    print(f"✓ Updated dataset description")
    
    # Update a row
    updated_row = client.update_dataset_row(
        dataset_id=dataset_id,
        dataset_row_id=row2_id,
        row={
            "dataSetRowInput": "What is Deep Learning? (Updated)",
            "dataSetRowExpectedAnswer": "Deep Learning uses neural networks with many layers to learn complex patterns.",
            "dataSetRowContextDocument": "DL is particularly effective for image and speech recognition."
        }
    )
    print(f"✓ Updated row 2")
    
    # Update expected source
    updated_source = client.update_expected_source(
        dataset_id=dataset_id,
        dataset_row_id=row1_id,
        expected_source_id=source1_id,
        expected_source_name="ML Fundamentals - Updated",
        expected_source_value="Updated source content about Machine Learning.",
        expected_source_extension="txt"
    )
    print(f"✓ Updated expected source")
    
    # Update filter variable
    updated_filter = client.update_filter_variable(
        dataset_id=dataset_id,
        dataset_row_id=row1_id,
        filter_variable_id=filter2_id,
        metadata_type="V",
        filter_variable_key="difficulty",
        filter_variable_value="intermediate",
        filter_variable_operator="="
    )
    print(f"✓ Updated filter variable")
    
    # Step 7: Cleanup
    print("\n[7/7] Cleaning up...")
    
    # Delete filter variables
    client.delete_filter_variable(dataset_id=dataset_id, dataset_row_id=row1_id, filter_variable_id=filter1_id)
    client.delete_filter_variable(dataset_id=dataset_id, dataset_row_id=row1_id, filter_variable_id=filter2_id)
    print(f"✓ Deleted filter variables")
    
    # Delete expected source
    client.delete_expected_source(dataset_id=dataset_id, dataset_row_id=row1_id, expected_source_id=source1_id)
    print(f"✓ Deleted expected source")
    
    # Delete rows
    client.delete_dataset_row(dataset_id=dataset_id, dataset_row_id=row1_id)
    client.delete_dataset_row(dataset_id=dataset_id, dataset_row_id=row2_id)
    print(f"✓ Deleted rows")
    
    # Delete dataset
    client.delete_dataset(dataset_id=dataset_id)
    print(f"✓ Deleted dataset")
    
    print("\n" + "="*60)
    print("Workflow completed successfully!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
