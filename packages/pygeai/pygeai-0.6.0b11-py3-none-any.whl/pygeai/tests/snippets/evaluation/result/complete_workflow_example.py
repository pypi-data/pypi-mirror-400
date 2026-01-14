"""
Complete Evaluation Result API Workflow Example

This example demonstrates how to retrieve and analyze evaluation results:
1. List all results for a plan
2. Get detailed results for each
3. Analyze performance metrics
4. Extract insights

Note: This is a read-only API. Results are created by executing evaluation plans.
"""

from pygeai.evaluation.result.clients import EvaluationResultClient


def main():
    # Initialize client
    client = EvaluationResultClient()
    
    print("="*70)
    print("Evaluation Result API Complete Workflow Example")
    print("="*70)
    
    # Step 1: List all results for an evaluation plan
    print("\n[1/4] Listing evaluation results for a plan...")
    evaluation_plan_id = "your-evaluation-plan-id"
    
    results = client.list_evaluation_results(evaluation_plan_id=evaluation_plan_id)
    
    if isinstance(results, list):
        print(f"✓ Found {len(results)} evaluation results")
    else:
        print(f"✓ Results: {results}")
        results = []
    
    # Step 2: Display summary of all results
    print("\n[2/4] Summary of all results:")
    print("-" * 70)
    
    total_cost = 0
    total_duration = 0
    status_counts = {}
    
    for i, result in enumerate(results, 1):
        result_id = result.get('evaluationResultId', 'Unknown')
        status = result.get('evaluationResultStatus', 'Unknown')
        cost = result.get('evaluationResultCost', 0)
        duration = result.get('evaluationResultDuration', 0)
        
        print(f"\n{i}. Result ID: {result_id}")
        print(f"   Status: {status}")
        print(f"   Cost: ${cost}")
        print(f"   Duration: {duration}ms")
        print(f"   Model: {result.get('evaluationResultModelName', 'N/A')}")
        print(f"   Provider: {result.get('evaluationResultProviderName', 'N/A')}")
        
        # Aggregate metrics
        total_cost += cost
        total_duration += duration
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Step 3: Get detailed results for the first result
    if results:
        print("\n[3/4] Getting detailed results for first evaluation...")
        first_result_id = results[0].get('evaluationResultId')
        
        detailed_result = client.get_evaluation_result(
            evaluation_result_id=first_result_id
        )
        
        print(f"✓ Retrieved detailed result: {detailed_result.get('evaluationResultId')}")
        
        # Display row-level details
        rows = detailed_result.get('rows', [])
        print(f"\n  Row-level results: {len(rows)} rows")
        
        successful_rows = 0
        failed_rows = 0
        row_costs = []
        
        for row in rows:
            row_status = row.get('evaluationResultRowStatus', 'Unknown')
            row_cost = row.get('evaluationResultRowCost', 0)
            
            if row_status == 'completed' or row_status == 'success':
                successful_rows += 1
            else:
                failed_rows += 1
            
            row_costs.append(row_cost)
        
        print(f"  Successful rows: {successful_rows}")
        print(f"  Failed rows: {failed_rows}")
        
        if row_costs:
            avg_row_cost = sum(row_costs) / len(row_costs)
            print(f"  Average row cost: ${avg_row_cost:.4f}")
        
        # Show sample row
        if rows:
            print(f"\n  Sample Row:")
            sample_row = rows[0]
            print(f"    Dataset Row ID: {sample_row.get('dataSetRowId')}")
            print(f"    Status: {sample_row.get('evaluationResultRowStatus')}")
            print(f"    Cost: ${sample_row.get('evaluationResultRowCost')}")
            print(f"    Start: {sample_row.get('evaluationResultRowStartDate')}")
            print(f"    End: {sample_row.get('evaluationResultRowEndDate')}")
            
            output = sample_row.get('evaluationResultRowOutput', '')
            if output:
                print(f"    Output (first 200 chars):")
                print(f"      {output[:200]}...")
    
    # Step 4: Display aggregated analytics
    print("\n[4/4] Aggregated Analytics:")
    print("-" * 70)
    print(f"Total Evaluations: {len(results)}")
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Total Duration: {total_duration}ms ({total_duration/1000:.2f}s)")
    
    if results:
        print(f"Average Cost per Evaluation: ${total_cost/len(results):.4f}")
        print(f"Average Duration per Evaluation: {total_duration/len(results):.0f}ms")
    
    print(f"\nStatus Distribution:")
    for status, count in status_counts.items():
        percentage = (count / len(results) * 100) if results else 0
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print("\n" + "="*70)
    print("Workflow completed successfully!")
    print("="*70)
    
    # Important note about field names
    print("\n⚠️  IMPORTANT NOTE:")
    print("The API responses contain typos in some field names:")
    print("  - evaluationResultAssitantRevision (missing 's' in Assistant)")
    print("  - evaluationResultChunckCount (should be Chunk)")
    print("  - evaluationResultChunckSize (should be Chunk)")
    print("  - evaluationResultaMaxTokens (lowercase 'a')")
    print("\nThese are API-level typos, not errors in our code.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
