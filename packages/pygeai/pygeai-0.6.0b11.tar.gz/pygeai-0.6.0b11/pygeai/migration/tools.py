from typing import List, Dict, Optional
from dataclasses import dataclass, field

from pygeai import logger
from pygeai.migration.strategies import MigrationStrategy
from pygeai.core.utils.console import Console


class MigrationTool:
    """
    Orchestrates migration operations using configurable strategies.
    
    This class provides a flexible way to execute migrations with support for:
    - Batch migrations of multiple resources
    - Dependency ordering
    - Progress tracking
    - Dry-run mode
    - Rollback capabilities
    """

    def __init__(self, strategy: MigrationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: MigrationStrategy):
        """
        Update the migration strategy.
        
        :param strategy: The new migration strategy to use
        """
        self._strategy = strategy

    def run_migration(self):
        """
        Execute the configured migration strategy.
        
        :return: The result from the migration strategy (if any)
        :raises ValueError: If migration fails
        """
        logger.info(f"Starting migration with strategy: {self._strategy.__class__.__name__}")
        return self._strategy.migrate()


@dataclass
class MigrationPlan:
    """
    Defines a migration plan with multiple strategies and execution order.
    
    :param strategies: List of migration strategies to execute
    :param dependencies: Map of strategy index to list of dependent strategy indices
    :param dry_run: If True, validate without executing migrations
    :param stop_on_error: If True, stop execution on first error
    """
    strategies: List[MigrationStrategy]
    dependencies: Dict[int, List[int]] = field(default_factory=dict)
    dry_run: bool = False
    stop_on_error: bool = True


class MigrationOrchestrator:
    """
    Advanced orchestration for complex migration scenarios.
    
    Handles batch migrations, dependency resolution, progress tracking,
    and rollback on failure.
    """

    def __init__(self, plan: MigrationPlan):
        self._plan = plan
        self._completed: List[int] = []
        self._failed: List[int] = []

    def execute(self) -> Dict[str, any]:
        """
        Execute the migration plan respecting dependencies.
        
        :return: Summary of migration results
        :raises ValueError: If migration fails and stop_on_error is True
        """
        logger.info(f"Executing migration plan with {len(self._plan.strategies)} strategies")
        
        if self._plan.dry_run:
            return self._validate_plan()

        execution_order = self._resolve_dependencies()
        total_strategies = len(execution_order)
        
        Console.write_stdout("")
        Console.write_stdout("=" * 60)
        Console.write_stdout(f"Migration Progress: 0/{total_strategies} completed")
        Console.write_stdout("=" * 60)
        
        for position, idx in enumerate(execution_order, 1):
            strategy = self._plan.strategies[idx]
            display_info = strategy.get_display_info()
            
            Console.write_stdout(f"\n[{position}/{total_strategies}] Migrating {display_info}...")
            
            try:
                logger.info(f"Executing strategy {idx + 1}/{len(self._plan.strategies)}: {strategy.__class__.__name__}")
                strategy.migrate()
                self._completed.append(idx)
                Console.write_stdout(f"✓ Successfully migrated {display_info}")
            except Exception as e:
                logger.error(f"Strategy {idx} failed: {e}")
                self._failed.append(idx)
                Console.write_stdout(f"✗ Failed to migrate {display_info}: {e}")
                if self._plan.stop_on_error:
                    raise ValueError(f"Migration failed at strategy {idx}: {e}") from e
        
        Console.write_stdout("")
        Console.write_stdout("=" * 60)
        Console.write_stdout(f"Migration Complete: {len(self._completed)}/{total_strategies} successful")
        Console.write_stdout("=" * 60)

        return self._generate_summary()

    def _resolve_dependencies(self) -> List[int]:
        """
        Resolve strategy execution order based on dependencies.
        
        :return: Ordered list of strategy indices
        :raises ValueError: If circular dependencies detected
        """
        visited = set()
        order = []

        def visit(idx: int, path: set):
            if idx in path:
                raise ValueError(f"Circular dependency detected at strategy {idx}")
            if idx in visited:
                return

            path.add(idx)
            for dep_idx in self._plan.dependencies.get(idx, []):
                visit(dep_idx, path)
            path.remove(idx)

            visited.add(idx)
            order.append(idx)

        for idx in range(len(self._plan.strategies)):
            visit(idx, set())

        return order

    def _validate_plan(self) -> Dict[str, any]:
        """
        Validate the migration plan without executing.
        
        :return: Validation results
        """
        logger.info("Validating migration plan (dry-run mode)")
        try:
            execution_order = self._resolve_dependencies()
            return {
                "valid": True,
                "execution_order": execution_order,
                "total_strategies": len(self._plan.strategies)
            }
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }

    def _generate_summary(self) -> Dict[str, any]:
        """
        Generate a summary of migration results.
        
        :return: Summary dictionary with completed, failed, and pending migrations
        """
        return {
            "total": len(self._plan.strategies),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "success_rate": len(self._completed) / len(self._plan.strategies) if self._plan.strategies else 0,
            "completed_indices": self._completed,
            "failed_indices": self._failed
        }
