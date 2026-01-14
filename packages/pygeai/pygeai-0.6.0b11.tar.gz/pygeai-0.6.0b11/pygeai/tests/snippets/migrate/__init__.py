"""
GEAI Migration Examples

This package contains comprehensive examples for migrating GEAI resources
between projects and instances using both CLI and Python SDK.

## Quick Import

Import specific modules:
    from pygeai.tests.snippets.migrate import agent_migration
    from pygeai.tests.snippets.migrate import project_migration

Import all examples:
    from pygeai.tests.snippets.migrate import *

## Available Modules

- project_migration:     Create projects and migrate usage limits (1 example)
- agent_migration:       Migrate agents between projects (3 examples)
- tool_migration:        Migrate tools between projects (2 examples)
- process_migration:     Migrate agentic processes (2 examples)
- assistant_migration:   Migrate RAG assistants (2 examples)
- orchestrator_examples: Complex multi-step workflows (3 examples)

## Documentation

See EXAMPLES_INDEX.md for a quick reference of all available examples.
See README.md for comprehensive usage guide and patterns.

## Example Usage

    from pygeai.tests.snippets.migrate.agent_migration import example_migrate_all_agents
    
    result = example_migrate_all_agents()
    print(result)
"""

__all__ = [
    'project_migration',
    'agent_migration',
    'tool_migration',
    'process_migration',
    'assistant_migration',
    'orchestrator_examples'
]
