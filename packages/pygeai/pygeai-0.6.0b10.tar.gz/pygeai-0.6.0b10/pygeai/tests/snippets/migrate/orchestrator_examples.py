"""
Migration Orchestrator Examples

Demonstrates how to orchestrate complex migrations with multiple strategies
and handle error scenarios.
"""

from pygeai.migration.strategies import (
    ProjectMigrationStrategy,
    AgentMigrationStrategy,
    ToolMigrationStrategy,
    RAGAssistantMigrationStrategy
)
from pygeai.migration.tools import MigrationOrchestrator


def example_orchestrated_migration():
    """
    Use the orchestrator to execute multiple migration strategies in sequence.
    This is useful for complex migrations with multiple resource types.
    """
    # First, create the project
    project_strategy = ProjectMigrationStrategy(
        from_api_key="source_org_key_abc123def456ghi789jkl012mno345pqr678",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_org_key_stu901vwx234yz567abc890def123ghi456jkl789",
        to_project_name="Orchestrated Migration Project",
        admin_email="admin@example.com"
    )
    
    # Create the orchestrator
    orchestrator = MigrationOrchestrator()
    
    # Add the project creation strategy
    orchestrator.add_strategy(project_strategy)
    
    # After project creation, we'll need the new project ID
    # The orchestrator will handle this automatically
    
    # Add agent migration strategy
    agent_strategy = AgentMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id=None,  # Will be filled by orchestrator after project creation
        agent_ids=None  # Migrate all agents
    )
    orchestrator.add_strategy(agent_strategy)
    
    # Add tool migration strategy
    tool_strategy = ToolMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id=None,  # Will be filled by orchestrator
        tool_ids=None  # Migrate all tools
    )
    orchestrator.add_strategy(tool_strategy)
    
    # Execute all strategies in order
    results = orchestrator.execute()
    
    print(f"Migration completed:")
    print(f"  Total strategies: {results['total']}")
    print(f"  Successful: {results['completed']}")
    print(f"  Failed: {results['failed']}")
    
    return results


def example_migration_with_error_handling():
    """
    Demonstrate proper error handling during migrations.
    """
    from pygeai.core.common.exceptions import MigrationException
    
    try:
        strategy = AgentMigrationStrategy(
            from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
            from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
            from_instance="https://api.test.example.ai",
            to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
            to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
            agent_ids=None
        )
        
        result = strategy.migrate()
        
        print(f"✓ Migration successful: {result['summary']}")
        
    except MigrationException as e:
        print(f"✗ Migration failed: {e}")
        print(f"  Details: {e.details}")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_full_migration_workflow():
    """
    Complete workflow: create project, migrate all resources, verify.
    """
    # Step 1: Create new project with usage limits
    print("Step 1: Creating new project...")
    project_strategy = ProjectMigrationStrategy(
        from_api_key="source_org_key_abc123def456ghi789jkl012mno345pqr678",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_org_key_stu901vwx234yz567abc890def123ghi456jkl789",
        to_project_name="Complete Migration",
        admin_email="admin@example.com"
    )
    
    project_result = project_strategy.migrate()
    new_project_id = project_result['project_id']
    print(f"✓ Project created: {new_project_id}")
    
    # Step 2: Migrate agents
    print("\nStep 2: Migrating agents...")
    agent_strategy = AgentMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id=new_project_id,
        agent_ids=None
    )
    agent_result = agent_strategy.migrate()
    print(f"✓ Migrated {len(agent_result['migrated_agents'])} agents")
    
    # Step 3: Migrate tools
    print("\nStep 3: Migrating tools...")
    tool_strategy = ToolMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id=new_project_id,
        tool_ids=None
    )
    tool_result = tool_strategy.migrate()
    print(f"✓ Migrated {len(tool_result['migrated_tools'])} tools")
    
    # Step 4: Migrate RAG assistants
    print("\nStep 4: Migrating RAG assistants...")
    assistant_strategy = RAGAssistantMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id=new_project_id,
        assistant_names=None
    )
    assistant_result = assistant_strategy.migrate()
    print(f"✓ Migrated {len(assistant_result['migrated_assistants'])} assistants")
    
    print("\n✓ Complete migration finished successfully!")
    
    return {
        'project': project_result,
        'agents': agent_result,
        'tools': tool_result,
        'assistants': assistant_result
    }


if __name__ == "__main__":
    print("Migration Orchestrator Examples")
    print("=" * 80)
    print("\nThese examples demonstrate complex migration workflows.")
    print("Uncomment to run specific examples:\n")
    
    # Uncomment to run specific examples:
    # example_orchestrated_migration()
    # example_migration_with_error_handling()
    # example_full_migration_workflow()
