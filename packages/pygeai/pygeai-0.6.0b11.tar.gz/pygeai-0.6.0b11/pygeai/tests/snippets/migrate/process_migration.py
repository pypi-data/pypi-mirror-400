"""
Agentic Process Migration Examples

Demonstrates how to migrate agentic processes between projects.
Uses project-scope API keys.
"""

from pygeai.migration.strategies import AgenticProcessMigrationStrategy


def example_migrate_all_processes():
    """
    Migrate all agentic processes from source project.
    """
    strategy = AgenticProcessMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        process_ids=None  # None for all processes
    )
    
    result = strategy.migrate()
    print(f"Migrated {len(result['migrated_processes'])} processes")
    
    return result


def example_migrate_specific_processes():
    """
    Migrate specific agentic processes by ID.
    """
    process_ids = [
        "4b5c6d7e-8f9g-0h1i-2j3k-4l5m6n7o8p9q",
        "5c6d7e8f-9g0h-1i2j-3k4l-5m6n7o8p9q0r"
    ]
    
    strategy = AgenticProcessMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        process_ids=process_ids
    )
    
    result = strategy.migrate()
    print(f"Migrated {len(result['migrated_processes'])} specific processes")
    
    return result


if __name__ == "__main__":
    print("Agentic Process Migration Examples")
    print("=" * 80)
    print("\nThese examples demonstrate agentic process migration patterns.")
    print("Uncomment to run specific examples:\n")
    
    # Uncomment to run specific examples:
    # example_migrate_all_processes()
    # example_migrate_specific_processes()
