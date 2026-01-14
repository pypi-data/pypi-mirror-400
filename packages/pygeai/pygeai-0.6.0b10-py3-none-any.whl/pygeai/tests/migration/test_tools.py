import unittest
from unittest.mock import Mock

from pygeai.migration.tools import MigrationTool, MigrationPlan, MigrationOrchestrator
from pygeai.migration.strategies import MigrationStrategy


class TestMigrationTool(unittest.TestCase):
    """
    python -m unittest pygeai.tests.migration.test_tools.TestMigrationTool
    """

    def setUp(self):
        self.mock_strategy = Mock(spec=MigrationStrategy)

    def test_migration_tool_initialization(self):
        tool = MigrationTool(self.mock_strategy)
        self.assertEqual(tool._strategy, self.mock_strategy)

    def test_migration_tool_set_strategy(self):
        tool = MigrationTool(self.mock_strategy)
        new_strategy = Mock(spec=MigrationStrategy)
        tool.set_strategy(new_strategy)
        self.assertEqual(tool._strategy, new_strategy)

    def test_migration_tool_run_migration(self):
        tool = MigrationTool(self.mock_strategy)
        tool.run_migration()
        self.mock_strategy.migrate.assert_called_once()


class TestMigrationPlan(unittest.TestCase):
    """
    python -m unittest pygeai.tests.migration.test_tools.TestMigrationPlan
    """

    def test_migration_plan_initialization(self):
        strategies = [Mock(spec=MigrationStrategy), Mock(spec=MigrationStrategy)]
        plan = MigrationPlan(strategies=strategies)
        self.assertEqual(len(plan.strategies), 2)
        self.assertEqual(plan.dependencies, {})
        self.assertFalse(plan.dry_run)
        self.assertTrue(plan.stop_on_error)

    def test_migration_plan_with_dependencies(self):
        strategies = [Mock(spec=MigrationStrategy), Mock(spec=MigrationStrategy)]
        dependencies = {1: [0]}
        plan = MigrationPlan(strategies=strategies, dependencies=dependencies)
        self.assertEqual(plan.dependencies, {1: [0]})


class TestMigrationOrchestrator(unittest.TestCase):
    """
    python -m unittest pygeai.tests.migration.test_tools.TestMigrationOrchestrator
    """

    def setUp(self):
        self.strategy1 = Mock(spec=MigrationStrategy)
        self.strategy2 = Mock(spec=MigrationStrategy)
        self.strategy3 = Mock(spec=MigrationStrategy)

    def test_orchestrator_simple_execution(self):
        plan = MigrationPlan(strategies=[self.strategy1, self.strategy2])
        orchestrator = MigrationOrchestrator(plan)
        
        result = orchestrator.execute()
        
        self.strategy1.migrate.assert_called_once()
        self.strategy2.migrate.assert_called_once()
        self.assertEqual(result['total'], 2)
        self.assertEqual(result['completed'], 2)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['success_rate'], 1.0)

    def test_orchestrator_with_dependencies(self):
        plan = MigrationPlan(
            strategies=[self.strategy1, self.strategy2, self.strategy3],
            dependencies={1: [0], 2: [1]}
        )
        orchestrator = MigrationOrchestrator(plan)
        
        result = orchestrator.execute()
        
        self.assertEqual(result['completed'], 3)
        self.assertEqual(result['completed_indices'], [0, 1, 2])

    def test_orchestrator_stop_on_error(self):
        self.strategy1.migrate.side_effect = Exception("Migration failed")
        plan = MigrationPlan(
            strategies=[self.strategy1, self.strategy2],
            stop_on_error=True
        )
        orchestrator = MigrationOrchestrator(plan)
        
        with self.assertRaises(ValueError) as context:
            orchestrator.execute()
        
        self.assertIn("Migration failed at strategy", str(context.exception))
        self.strategy1.migrate.assert_called_once()
        self.strategy2.migrate.assert_not_called()

    def test_orchestrator_continue_on_error(self):
        self.strategy1.migrate.side_effect = Exception("Migration failed")
        plan = MigrationPlan(
            strategies=[self.strategy1, self.strategy2],
            stop_on_error=False
        )
        orchestrator = MigrationOrchestrator(plan)
        
        result = orchestrator.execute()
        
        self.strategy1.migrate.assert_called_once()
        self.strategy2.migrate.assert_called_once()
        self.assertEqual(result['completed'], 1)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['success_rate'], 0.5)

    def test_orchestrator_dry_run(self):
        plan = MigrationPlan(
            strategies=[self.strategy1, self.strategy2],
            dry_run=True
        )
        orchestrator = MigrationOrchestrator(plan)
        
        result = orchestrator.execute()
        
        self.strategy1.migrate.assert_not_called()
        self.strategy2.migrate.assert_not_called()
        self.assertTrue(result['valid'])
        self.assertEqual(result['execution_order'], [0, 1])

    def test_orchestrator_circular_dependency(self):
        plan = MigrationPlan(
            strategies=[self.strategy1, self.strategy2],
            dependencies={0: [1], 1: [0]}
        )
        orchestrator = MigrationOrchestrator(plan)
        
        with self.assertRaises(ValueError) as context:
            orchestrator.execute()
        
        self.assertIn("Circular dependency", str(context.exception))

    def test_orchestrator_dry_run_circular_dependency(self):
        plan = MigrationPlan(
            strategies=[self.strategy1, self.strategy2],
            dependencies={0: [1], 1: [0]},
            dry_run=True
        )
        orchestrator = MigrationOrchestrator(plan)
        
        result = orchestrator.execute()
        
        self.assertFalse(result['valid'])
        self.assertIn("Circular dependency", result['error'])


if __name__ == '__main__':
    unittest.main()
