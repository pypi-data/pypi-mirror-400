"""
Complete Evaluation Plan API Workflow Example

This example demonstrates a full workflow using the Evaluation Plan API:
1. Query available system metrics
2. Create an evaluation plan
3. Add system metrics
4. Update the plan
5. Execute the plan
6. Cleanup
"""

from pygeai.evaluation.plan.clients import EvaluationPlanClient


def main():
    # Initialize client
    client = EvaluationPlanClient()
    
    print("="*60)
    print("Evaluation Plan API Complete Workflow Example")
    print("="*60)
    
    # Step 1: List available system metrics
    print("\n[1/7] Listing available system metrics...")
    metrics = client.list_system_metrics()
    print(f"✓ Available metrics: {metrics}")
    
    # Get details of a specific metric
    if metrics and 'systemMetrics' in metrics and len(metrics['systemMetrics']) > 0:
        first_metric_id = metrics['systemMetrics'][0].get('systemMetricId')
        metric_details = client.get_system_metric(system_metric_id=first_metric_id)
        print(f"✓ Sample metric details: {metric_details}")
    
    # Step 2: Create an evaluation plan
    print("\n[2/7] Creating evaluation plan...")
    plan = client.create_evaluation_plan(
        name="AI Assistant Performance Test",
        type="TextPromptAssistant",
        assistant_id="your-assistant-id",
        assistant_name="Test Assistant",
        assistant_revision="1.0",
        dataset_id="your-dataset-id",
        system_metrics=[
            {
                "systemMetricId": "accuracy",
                "systemMetricWeight": 0.6
            },
            {
                "systemMetricId": "fluency",
                "systemMetricWeight": 0.4
            }
        ]
    )
    plan_id = plan.get('evaluationPlanId')
    print(f"✓ Created evaluation plan: {plan_id}")
    
    # Step 3: Get the plan details
    print("\n[3/7] Retrieving plan details...")
    plan_details = client.get_evaluation_plan(evaluation_plan_id=plan_id)
    print(f"✓ Plan name: {plan_details.get('evaluationPlanName')}")
    print(f"✓ Plan type: {plan_details.get('evaluationPlanType')}")
    print(f"✓ Number of metrics: {len(plan_details.get('systemMetrics', []))}")
    
    # Step 4: List plan's system metrics
    print("\n[4/7] Listing plan's system metrics...")
    plan_metrics = client.list_evaluation_plan_system_metrics(evaluation_plan_id=plan_id)
    print(f"✓ Plan metrics: {plan_metrics}")
    
    # Step 5: Add a new metric to the plan
    print("\n[5/7] Adding new system metric to plan...")
    new_metric = client.add_evaluation_plan_system_metric(
        evaluation_plan_id=plan_id,
        system_metric_id="relevance",
        system_metric_weight=0.5
    )
    print(f"✓ Added metric: {new_metric}")
    
    # Step 6: Update a metric's weight
    print("\n[6/7] Updating metric weight...")
    updated_metric = client.update_evaluation_plan_system_metric(
        evaluation_plan_id=plan_id,
        system_metric_id="accuracy",
        system_metric_weight=0.8
    )
    print(f"✓ Updated metric weight")
    
    # Get specific metric details
    metric_detail = client.get_evaluation_plan_system_metric(
        evaluation_plan_id=plan_id,
        system_metric_id="accuracy"
    )
    print(f"✓ Metric details: {metric_detail}")
    
    # Step 7: Update the plan itself
    print("\n[7/7] Updating evaluation plan...")
    updated_plan = client.update_evaluation_plan(
        evaluation_plan_id=plan_id,
        name="Updated Performance Test",
        assistant_revision="2.0"
    )
    print(f"✓ Updated plan")
    
    # Execute the evaluation plan
    print("\n[EXECUTE] Running evaluation plan...")
    execution = client.execute_evaluation_plan(evaluation_plan_id=plan_id)
    print(f"✓ Execution started")
    print(f"  Execution ID: {execution.get('executionId')}")
    print(f"  Status: {execution.get('status')}")
    
    # Cleanup
    print("\n[CLEANUP] Cleaning up...")
    
    # Delete metrics
    client.delete_evaluation_plan_system_metric(
        evaluation_plan_id=plan_id,
        system_metric_id="relevance"
    )
    print(f"✓ Deleted added metric")
    
    # Delete the plan
    client.delete_evaluation_plan(evaluation_plan_id=plan_id)
    print(f"✓ Deleted evaluation plan")
    
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
