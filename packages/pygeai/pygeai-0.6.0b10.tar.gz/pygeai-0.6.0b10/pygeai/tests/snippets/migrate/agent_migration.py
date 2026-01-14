"""
Agent Migration Examples

Demonstrates how to migrate agents between projects.
Uses project-scope API keys.
"""

from pygeai.migration.strategies import AgentMigrationStrategy


def example_migrate_specific_agents():
    """
    Migrate specific agents by ID to an existing project.
    Uses project-scope API keys.
    """
    agent_ids = [
        "9d8e7f6g-5h4i-3j2k-1l0m-9n8o7p6q5r4s",
        "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p"
    ]
    
    strategy = AgentMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        agent_ids=agent_ids
    )
    
    result = strategy.migrate()
    
    print(f"Migrated {len(result['migrated_agents'])} agents")
    for agent in result['migrated_agents']:
        print(f"  - {agent['name']} (ID: {agent['id']})")
    
    return result


def example_migrate_all_agents():
    """
    Automatically discover and migrate all agents from source project.
    """
    strategy = AgentMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        agent_ids=None  # None means "all agents"
    )
    
    result = strategy.migrate()
    print(f"Migrated all {len(result['migrated_agents'])} agents")
    
    return result


def example_custom_filtered_migration():
    """
    Create a custom migration that only migrates agents with specific tags
    or matching certain criteria.
    """
    from pygeai.lab.managers import AILabManager
    
    # Initialize managers for source and destination
    source_lab = AILabManager(
        api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        instance="https://api.test.example.ai"
    )
    
    # Get all agents and filter
    all_agents = source_lab.get_agent_list()
    
    # Custom filter: only migrate agents with "production" in their name
    filtered_agent_ids = [
        agent.id for agent in all_agents.agents 
        if "production" in agent.name.lower()
    ]
    
    print(f"Found {len(filtered_agent_ids)} agents matching filter")
    
    # Now migrate only the filtered agents
    strategy = AgentMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        agent_ids=filtered_agent_ids
    )
    
    result = strategy.migrate()
    print(f"Migrated {len(result['migrated_agents'])} filtered agents")
    
    return result


if __name__ == "__main__":
    print("Agent Migration Examples")
    print("=" * 80)
    print("\nThese examples demonstrate various agent migration patterns.")
    print("Uncomment to run specific examples:\n")
    
    # Uncomment to run specific examples:
    # example_migrate_specific_agents()
    # example_migrate_all_agents()
    # example_custom_filtered_migration()
