"""
RAG Assistant Migration Examples

Demonstrates how to migrate RAG assistants between projects.
Uses project-scope API keys.
"""

from pygeai.migration.strategies import RAGAssistantMigrationStrategy


def example_migrate_all_assistants():
    """
    Migrate all RAG assistants from source project.
    """
    strategy = RAGAssistantMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        assistant_names=None  # None for all assistants
    )
    
    result = strategy.migrate()
    print(f"Migrated {len(result['migrated_assistants'])} assistants")
    
    return result


def example_migrate_specific_assistants():
    """
    Migrate specific RAG assistants by name.
    """
    assistant_names = [
        "Customer Support Assistant",
        "Product Documentation Assistant"
    ]
    
    strategy = RAGAssistantMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        assistant_names=assistant_names
    )
    
    result = strategy.migrate()
    print(f"Migrated {len(result['migrated_assistants'])} specific assistants")
    
    return result


if __name__ == "__main__":
    print("RAG Assistant Migration Examples")
    print("=" * 80)
    print("\nThese examples demonstrate RAG assistant migration patterns.")
    print("Uncomment to run specific examples:\n")
    
    # Uncomment to run specific examples:
    # example_migrate_all_assistants()
    # example_migrate_specific_assistants()
