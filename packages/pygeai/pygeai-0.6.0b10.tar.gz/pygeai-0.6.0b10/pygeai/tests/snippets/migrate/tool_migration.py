"""
Tool Migration Examples

Demonstrates how to migrate tools between projects.
Uses project-scope API keys.
"""

from pygeai.migration.strategies import ToolMigrationStrategy


def example_migrate_specific_tools():
    """
    Migrate specific tools by ID.
    """
    tool_ids = [
        "2a3b4c5d-6e7f-8g9h-0i1j-2k3l4m5n6o7p",
        "3b4c5d6e-7f8g-9h0i-1j2k-3l4m5n6o7p8q"
    ]
    
    strategy = ToolMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        tool_ids=tool_ids
    )
    
    result = strategy.migrate()
    print(f"Migrated {len(result['migrated_tools'])} tools")
    
    return result


def example_migrate_all_tools():
    """
    Migrate all tools from source project.
    """
    strategy = ToolMigrationStrategy(
        from_api_key="source_project_key_123abc456def789ghi012jkl345mno678pqr901",
        from_project_id="7x8y9z0a-1b2c-3d4e-5f6g-7h8i9j0k1l2m",
        from_instance="https://api.test.example.ai",
        to_api_key="dest_project_key_789stu012vwx345yz678abc901def234ghi567",
        to_project_id="3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
        to_instance="https://api.prod.example.ai",
        tool_ids=None  # None means "all tools"
    )
    
    result = strategy.migrate()
    print(f"Migrated all {len(result['migrated_tools'])} tools")
    
    return result


if __name__ == "__main__":
    print("Tool Migration Examples")
    print("=" * 80)
    print("\nThese examples demonstrate tool migration patterns.")
    print("Uncomment to run specific examples:\n")
    
    # Uncomment to run specific examples:
    # example_migrate_specific_tools()
    # example_migrate_all_tools()
