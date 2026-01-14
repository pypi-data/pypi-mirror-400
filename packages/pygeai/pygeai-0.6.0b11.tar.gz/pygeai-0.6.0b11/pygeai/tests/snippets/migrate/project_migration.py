"""
Project Migration Examples

Demonstrates how to create new projects and migrate usage limits.
Requires organization-scope API keys.
"""

from pygeai.migration.strategies import ProjectMigrationStrategy


def example_create_project_with_usage_limits():
    """
    Create a new project and migrate usage limits from an existing project.
    Requires organization-scope API keys.
    """
    strategy = ProjectMigrationStrategy(
        from_api_key="source_org_key_abc123def456ghi789jkl012mno345pqr678",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_org_key_stu901vwx234yz567abc890def123ghi456jkl789",
        to_project_name="New Migrated Project",
        admin_email="admin@example.com",
        to_instance="https://api.prod.example.ai"  # Optional: different instance
    )
    
    # Execute the migration
    result = strategy.migrate()
    
    print(f"Project created with ID: {result['project_id']}")
    print(f"Migration result: {result}")
    
    return result


if __name__ == "__main__":
    print("Project Migration Example")
    print("=" * 80)
    print("\nThis example demonstrates creating a new project with usage limits.")
    print("Uncomment to run:\n")
    
    # Uncomment to run:
    # example_create_project_with_usage_limits()
