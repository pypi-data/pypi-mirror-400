from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from types import FrameType
from pygeai.dbg.debugger import Debugger, Breakpoint


class TestBreakpoint(TestCase):
    """Test Breakpoint class."""
    
    def test_breakpoint_creation(self):
        bp = Breakpoint(module="test.module", function_name="test_func")
        self.assertEqual(bp.module, "test.module")
        self.assertEqual(bp.function_name, "test_func")
        self.assertTrue(bp.enabled)
        self.assertEqual(bp.hit_count, 0)
        self.assertIsNone(bp.condition)
    
    def test_breakpoint_matches_exact(self):
        bp = Breakpoint(module="test.module", function_name="test_func")
        self.assertTrue(bp.matches("test.module", "test_func"))
        self.assertFalse(bp.matches("other.module", "test_func"))
        self.assertFalse(bp.matches("test.module", "other_func"))
    
    def test_breakpoint_matches_wildcard_module(self):
        bp = Breakpoint(module=None, function_name="test_func")
        self.assertTrue(bp.matches("any.module", "test_func"))
        self.assertTrue(bp.matches("other.module", "test_func"))
        self.assertFalse(bp.matches("any.module", "other_func"))
    
    def test_breakpoint_matches_wildcard_function(self):
        bp = Breakpoint(module="test.module", function_name=None)
        self.assertTrue(bp.matches("test.module", "any_func"))
        self.assertTrue(bp.matches("test.module", "other_func"))
        self.assertFalse(bp.matches("other.module", "any_func"))
    
    def test_breakpoint_disabled(self):
        bp = Breakpoint(module="test.module", function_name="test_func", enabled=False)
        self.assertFalse(bp.matches("test.module", "test_func"))
    
    def test_breakpoint_str(self):
        bp = Breakpoint(module="test.module", function_name="test_func")
        bp.hit_count = 5
        self.assertIn("test.module:test_func", str(bp))
        self.assertIn("enabled", str(bp))
        self.assertIn("5", str(bp))
    
    def test_breakpoint_with_condition(self):
        bp = Breakpoint(module="test.module", function_name="test_func", condition="x > 10")
        self.assertEqual(bp.condition, "x > 10")
        self.assertIn("if x > 10", str(bp))


class TestDebugger(TestCase):
    """Test Debugger class."""

    def setUp(self):
        self.logging_patch = patch('pygeai.dbg.debugger.logging')
        self.mock_logging = self.logging_patch.start()
        self.mock_logger = MagicMock()
        self.mock_logging.getLogger.return_value = self.mock_logger
        
        self.console_patch = patch('pygeai.dbg.debugger.Console')
        self.mock_console = self.console_patch.start()
        self.mock_console.write_stdout = MagicMock()
        
        self.readline_patch = patch('pygeai.dbg.debugger.readline')
        self.mock_readline = self.readline_patch.start()

    def tearDown(self):
        self.logging_patch.stop()
        self.console_patch.stop()
        self.readline_patch.stop()

    def test_debugger_init_default(self):
        debugger = Debugger()
        self.assertEqual(len(debugger.breakpoints), 0)
        self.assertFalse(debugger.paused)
        self.assertIsNone(debugger.current_frame)
        self.assertEqual(debugger.module_filter, "pygeai")
        self.assertEqual(len(debugger.frame_stack), 0)

    def test_debugger_init_custom_target(self):
        def custom_target():
            pass
        
        debugger = Debugger(target=custom_target, module_filter="custom")
        self.assertEqual(debugger.target, custom_target)
        self.assertEqual(debugger.module_filter, "custom")

    def test_add_breakpoint_module_only(self):
        debugger = Debugger()
        bp = debugger.add_breakpoint(module="pygeai.cli.geai")
        self.assertEqual(len(debugger.breakpoints), 1)
        self.assertEqual(bp.module, "pygeai.cli.geai")
        self.assertIsNone(bp.function_name)
        self.assertTrue(bp.enabled)

    def test_add_breakpoint_function_only(self):
        debugger = Debugger()
        bp = debugger.add_breakpoint(function_name="main")
        self.assertEqual(len(debugger.breakpoints), 1)
        self.assertIsNone(bp.module)
        self.assertEqual(bp.function_name, "main")

    def test_add_breakpoint_both(self):
        debugger = Debugger()
        bp = debugger.add_breakpoint(module="pygeai.cli.geai", function_name="main")
        self.assertEqual(len(debugger.breakpoints), 1)
        self.assertEqual(bp.module, "pygeai.cli.geai")
        self.assertEqual(bp.function_name, "main")

    def test_add_breakpoint_with_condition(self):
        debugger = Debugger()
        bp = debugger.add_breakpoint(module="test", function_name="func", condition="x > 10")
        self.assertEqual(bp.condition, "x > 10")

    def test_add_breakpoint_duplicate(self):
        debugger = Debugger()
        bp1 = debugger.add_breakpoint(module="test", function_name="func")
        bp2 = debugger.add_breakpoint(module="test", function_name="func")
        self.assertEqual(bp1, bp2)
        self.assertEqual(len(debugger.breakpoints), 1)

    def test_remove_breakpoint(self):
        debugger = Debugger()
        debugger.add_breakpoint(module="test", function_name="func")
        self.assertEqual(len(debugger.breakpoints), 1)
        
        result = debugger.remove_breakpoint(module="test", function_name="func")
        self.assertTrue(result)
        self.assertEqual(len(debugger.breakpoints), 0)

    def test_remove_breakpoint_not_found(self):
        debugger = Debugger()
        result = debugger.remove_breakpoint(module="test", function_name="func")
        self.assertFalse(result)

    def test_list_breakpoints(self):
        debugger = Debugger()
        debugger.add_breakpoint(module="test1", function_name="func1")
        debugger.add_breakpoint(module="test2", function_name="func2")
        
        bps = debugger.list_breakpoints()
        self.assertEqual(len(bps), 2)

    def test_enable_disable_breakpoint(self):
        debugger = Debugger()
        debugger.add_breakpoint(module="test", function_name="func")
        
        result = debugger.disable_breakpoint(module="test", function_name="func")
        self.assertTrue(result)
        bp = debugger.breakpoints[("test", "func")]
        self.assertFalse(bp.enabled)
        
        result = debugger.enable_breakpoint(module="test", function_name="func")
        self.assertTrue(result)
        self.assertTrue(bp.enabled)

    def test_clear_breakpoints(self):
        debugger = Debugger()
        debugger.add_breakpoint(module="test1", function_name="func1")
        debugger.add_breakpoint(module="test2", function_name="func2")
        self.assertEqual(len(debugger.breakpoints), 2)
        
        debugger.clear_breakpoints()
        self.assertEqual(len(debugger.breakpoints), 0)

    def test_reset(self):
        debugger = Debugger()
        debugger.add_breakpoint(module="test", function_name="func")
        debugger.paused = True
        debugger.step_mode = "step"
        
        debugger.reset()
        self.assertEqual(len(debugger.breakpoints), 0)
        self.assertFalse(debugger.paused)
        self.assertIsNone(debugger.step_mode)

    def test_should_trace_module(self):
        debugger = Debugger(module_filter="pygeai")
        self.assertTrue(debugger._should_trace_module("pygeai.cli"))
        self.assertTrue(debugger._should_trace_module("pygeai.core"))
        self.assertFalse(debugger._should_trace_module("other.module"))
        self.assertFalse(debugger._should_trace_module(None))

    def test_check_condition_true(self):
        debugger = Debugger()
        bp = Breakpoint(condition="x > 5")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_locals = {"x": 10}
        mock_frame.f_globals = {}
        
        result = debugger._check_condition(bp, mock_frame)
        self.assertTrue(result)

    def test_check_condition_false(self):
        debugger = Debugger()
        bp = Breakpoint(condition="x > 5")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_locals = {"x": 3}
        mock_frame.f_globals = {}
        
        result = debugger._check_condition(bp, mock_frame)
        self.assertFalse(result)

    def test_check_condition_no_condition(self):
        debugger = Debugger()
        bp = Breakpoint()
        
        mock_frame = MagicMock(spec=FrameType)
        result = debugger._check_condition(bp, mock_frame)
        self.assertTrue(result)

    def test_check_condition_error(self):
        debugger = Debugger()
        bp = Breakpoint(condition="invalid syntax !!!")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_locals = {}
        mock_frame.f_globals = {}
        
        result = debugger._check_condition(bp, mock_frame)
        self.assertFalse(result)

    def test_build_frame_stack(self):
        debugger = Debugger()
        
        frame3 = MagicMock(spec=FrameType)
        frame3.f_back = None
        
        frame2 = MagicMock(spec=FrameType)
        frame2.f_back = frame3
        
        frame1 = MagicMock(spec=FrameType)
        frame1.f_back = frame2
        
        stack = debugger._build_frame_stack(frame1)
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack[0], frame1)
        self.assertEqual(stack[1], frame2)
        self.assertEqual(stack[2], frame3)

    def test_trace_function_ignores_non_filtered_modules(self):
        debugger = Debugger(module_filter="pygeai")
        debugger.add_breakpoint(function_name="main")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "other.module"}
        mock_frame.f_code.co_name = "main"
        
        result = debugger.trace_function(mock_frame, "call", None)
        self.assertIsNone(result)
        self.assertFalse(debugger.paused)

    def test_trace_function_breakpoint_hit(self):
        debugger = Debugger(module_filter="pygeai")
        debugger.add_breakpoint(module="pygeai.cli.geai", function_name="main")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "pygeai.cli.geai"}
        mock_frame.f_code.co_name = "main"
        mock_frame.f_code.co_filename = __file__
        mock_frame.f_lineno = 1
        mock_frame.f_back = None
        
        with patch('builtins.input', return_value="continue"):
            with patch.object(debugger, '_get_source_lines', return_value=[(1, "test")]):
                result = debugger.trace_function(mock_frame, "call", None)
                self.assertIsNotNone(result)
                bp = debugger.breakpoints[("pygeai.cli.geai", "main")]
                self.assertEqual(bp.hit_count, 1)

    def test_trace_function_disabled_breakpoint(self):
        debugger = Debugger(module_filter="pygeai")
        debugger.add_breakpoint(module="pygeai.cli.geai", function_name="main")
        debugger.disable_breakpoint(module="pygeai.cli.geai", function_name="main")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "pygeai.cli.geai"}
        mock_frame.f_code.co_name = "main"
        
        result = debugger.trace_function(mock_frame, "call", None)
        self.assertIsNotNone(result)
        self.assertFalse(debugger.paused)

    def test_trace_function_conditional_breakpoint_met(self):
        debugger = Debugger(module_filter="pygeai")
        debugger.add_breakpoint(module="pygeai.test", function_name="func", condition="x > 5")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "pygeai.test"}
        mock_frame.f_locals = {"x": 10}
        mock_frame.f_code.co_name = "func"
        mock_frame.f_code.co_filename = __file__
        mock_frame.f_lineno = 1
        mock_frame.f_back = None
        
        with patch('builtins.input', return_value="continue"):
            with patch.object(debugger, '_get_source_lines', return_value=[(1, "test")]):
                result = debugger.trace_function(mock_frame, "call", None)
                bp = debugger.breakpoints[("pygeai.test", "func")]
                self.assertEqual(bp.hit_count, 1)

    def test_trace_function_conditional_breakpoint_not_met(self):
        debugger = Debugger(module_filter="pygeai")
        debugger.add_breakpoint(module="pygeai.test", function_name="func", condition="x > 5")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "pygeai.test"}
        mock_frame.f_locals = {"x": 3}
        mock_frame.f_code.co_name = "func"
        
        result = debugger.trace_function(mock_frame, "call", None)
        bp = debugger.breakpoints[("pygeai.test", "func")]
        self.assertEqual(bp.hit_count, 0)
        self.assertFalse(debugger.paused)

    def test_move_frame_up(self):
        debugger = Debugger()
        
        frame2 = MagicMock(spec=FrameType)
        frame2.f_globals = {"__name__": "module2"}
        frame2.f_code.co_name = "func2"
        
        frame1 = MagicMock(spec=FrameType)
        frame1.f_globals = {"__name__": "module1"}
        frame1.f_code.co_name = "func1"
        
        debugger.frame_stack = [frame1, frame2]
        debugger.current_frame_index = 0
        debugger.current_frame = frame1
        
        result = debugger._move_frame(1)
        self.assertTrue(result)
        self.assertEqual(debugger.current_frame_index, 1)
        self.assertEqual(debugger.current_frame, frame2)

    def test_move_frame_down(self):
        debugger = Debugger()
        
        frame2 = MagicMock(spec=FrameType)
        frame2.f_globals = {"__name__": "module2"}
        frame2.f_code.co_name = "func2"
        
        frame1 = MagicMock(spec=FrameType)
        frame1.f_globals = {"__name__": "module1"}
        frame1.f_code.co_name = "func1"
        
        debugger.frame_stack = [frame1, frame2]
        debugger.current_frame_index = 1
        debugger.current_frame = frame2
        
        result = debugger._move_frame(-1)
        self.assertTrue(result)
        self.assertEqual(debugger.current_frame_index, 0)
        self.assertEqual(debugger.current_frame, frame1)

    def test_move_frame_out_of_bounds(self):
        debugger = Debugger()
        
        frame1 = MagicMock(spec=FrameType)
        frame1.f_globals = {"__name__": "module1"}
        frame1.f_code.co_name = "func1"
        
        debugger.frame_stack = [frame1]
        debugger.current_frame_index = 0
        debugger.current_frame = frame1
        
        result = debugger._move_frame(1)
        self.assertFalse(result)
        self.assertEqual(debugger.current_frame_index, 0)

    def test_run_successful(self):
        debugger = Debugger()
        with patch('sys.settrace') as mock_settrace:
            with patch.object(debugger, 'target') as mock_target:
                debugger.run()
                mock_target.assert_called_once()
                self.assertEqual(mock_settrace.call_count, 2)

    def test_run_with_exception(self):
        debugger = Debugger()
        with patch('sys.settrace') as mock_settrace:
            with patch.object(debugger, 'target', side_effect=Exception("Test error")):
                with self.assertRaises(Exception):
                    debugger.run()
                self.assertEqual(mock_settrace.call_count, 2)


class TestDebuggerCommands(TestCase):
    """Test debugger interactive commands."""
    
    def setUp(self):
        self.logging_patch = patch('pygeai.dbg.debugger.logging')
        self.mock_logging = self.logging_patch.start()
        self.mock_logger = MagicMock()
        self.mock_logging.getLogger.return_value = self.mock_logger
        
        self.console_patch = patch('pygeai.dbg.debugger.Console')
        self.mock_console = self.console_patch.start()
        
        self.readline_patch = patch('pygeai.dbg.debugger.readline')
        self.mock_readline = self.readline_patch.start()
        
        self.pprint_patch = patch('pygeai.dbg.debugger.pprint')
        self.mock_pprint = self.pprint_patch.start()

    def tearDown(self):
        self.logging_patch.stop()
        self.console_patch.stop()
        self.readline_patch.stop()
        self.pprint_patch.stop()

    def test_handle_breakpoint_continue(self):
        debugger = Debugger()
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "test"}
        mock_frame.f_code.co_name = "func"
        mock_frame.f_lineno = 10
        mock_frame.f_back = None
        
        with patch('builtins.input', side_effect=["c"]):
            with patch.object(debugger, '_get_source_lines', return_value=[(10, "test")]):
                debugger.handle_breakpoint(mock_frame)

    def test_handle_breakpoint_quit(self):
        debugger = Debugger()
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "test"}
        mock_frame.f_code.co_name = "func"
        mock_frame.f_lineno = 10
        
        with patch('builtins.input', return_value="q"):
            with patch.object(debugger, '_get_source_lines', return_value=[(10, "test")]):
                with self.assertRaises(SystemExit):
                    debugger.handle_breakpoint(mock_frame)

    def test_handle_breakpoint_print_expression(self):
        debugger = Debugger()
        debugger.current_frame = MagicMock(spec=FrameType)
        debugger.current_frame.f_globals = {"__name__": "test"}
        debugger.current_frame.f_locals = {"x": 42}
        debugger.current_frame.f_code.co_name = "func"
        debugger.current_frame.f_lineno = 10
        debugger.current_frame.f_back = None
        debugger.frame_stack = [debugger.current_frame]
        debugger.current_frame_index = 0
        
        with patch('builtins.input', side_effect=["p x", "c"]):
            with patch.object(debugger, '_get_source_lines', return_value=[(10, "test")]):
                debugger.handle_breakpoint(debugger.current_frame)
                calls = [str(call) for call in self.mock_console.write_stdout.call_args_list]
                self.assertTrue(any("42" in str(call) for call in calls))

    def test_handle_breakpoint_list_breakpoints(self):
        debugger = Debugger()
        debugger.add_breakpoint(module="test", function_name="func")
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "test"}
        mock_frame.f_code.co_name = "func"
        mock_frame.f_lineno = 10
        
        with patch('builtins.input', side_effect=["b", "c"]):
            with patch.object(debugger, '_get_source_lines', return_value=[(10, "test")]):
                debugger.handle_breakpoint(mock_frame)
                self.mock_console.write_stdout.assert_any_call("  1. test:func (enabled, hits: 0)")

    def test_handle_breakpoint_add_breakpoint(self):
        debugger = Debugger()
        
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "test"}
        mock_frame.f_code.co_name = "func"
        mock_frame.f_lineno = 10
        
        with patch('builtins.input', side_effect=["b new_func", "c"]):
            with patch.object(debugger, '_get_source_lines', return_value=[(10, "test")]):
                debugger.handle_breakpoint(mock_frame)
                self.assertEqual(len(debugger.breakpoints), 1)
                self.assertIn((None, "new_func"), debugger.breakpoints)

    def test_handle_breakpoint_keyboard_interrupt(self):
        debugger = Debugger()
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "test"}
        mock_frame.f_code.co_name = "func"
        mock_frame.f_lineno = 10
        
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            with patch.object(debugger, '_get_source_lines', return_value=[(10, "test")]):
                debugger.handle_breakpoint(mock_frame)

    def test_handle_breakpoint_eof(self):
        debugger = Debugger()
        mock_frame = MagicMock(spec=FrameType)
        mock_frame.f_globals = {"__name__": "test"}
        mock_frame.f_code.co_name = "func"
        mock_frame.f_lineno = 10
        
        with patch('builtins.input', side_effect=EOFError()):
            with patch.object(debugger, '_get_source_lines', return_value=[(10, "test")]):
                with self.assertRaises(SystemExit):
                    debugger.handle_breakpoint(mock_frame)
