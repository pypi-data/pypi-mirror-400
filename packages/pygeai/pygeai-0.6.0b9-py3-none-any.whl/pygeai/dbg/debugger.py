import logging
import sys
import inspect
import readline
import pprint
from types import FrameType
from typing import Optional, Any, Callable, Set, Dict, List, Tuple
from dataclasses import dataclass, field

from pygeai.cli.geai import main as geai
from pygeai.core.utils.console import Console


@dataclass
class Breakpoint:
    """Represents a breakpoint with optional conditions."""
    module: Optional[str] = None
    function_name: Optional[str] = None
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0
    
    def __hash__(self):
        return hash((self.module, self.function_name))
    
    def __eq__(self, other):
        if not isinstance(other, Breakpoint):
            return False
        return self.module == other.module and self.function_name == other.function_name
    
    def matches(self, module: str, func_name: str) -> bool:
        """Check if this breakpoint matches the given module and function."""
        if not self.enabled:
            return False
        module_match = self.module is None or self.module == module
        func_match = self.function_name is None or self.function_name == func_name
        return module_match and func_match
    
    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        cond = f" [if {self.condition}]" if self.condition else ""
        return f"{self.module or '*'}:{self.function_name or '*'} ({status}, hits: {self.hit_count}){cond}"


class Debugger:
    """
    A debugger for the GEAI application to trace and control execution flow.

    This class implements a custom debugging mechanism using Python's `sys.settrace` to intercept function calls
    and pause execution at specified breakpoints. Breakpoints can be set for specific modules or functions, allowing
    developers to inspect local variables, execute arbitrary code in the current context, and control program flow
    through an interactive command interface.
    
    Features:
    - Module filtering for performance (only traces pygeai modules by default)
    - Breakpoint management (add, list, remove, enable/disable, conditional)
    - Stack navigation (up/down frames)
    - Stepping (step-into, step-over, step-out)
    - Variable inspection with pretty-printing
    - Source code display
    - Stack trace viewing
    - Readline support for command history
    """

    def __init__(self, target: Optional[Callable] = None, module_filter: str = "pygeai"):
        """
        Initialize the debugger.
        
        Args:
            target: The callable to debug. If None, defaults to pygeai.cli.geai.main
            module_filter: Only trace modules starting with this prefix (for performance)
        """
        self.target = target or geai
        self.module_filter = module_filter
        self._setup_logging()
        self.logger = logging.getLogger('geai.dbg')
        
        self.breakpoints: Dict[Tuple[Optional[str], Optional[str]], Breakpoint] = {}
        self.paused: bool = False
        self.current_frame: Optional[FrameType] = None
        self.frame_stack: List[FrameType] = []
        self.current_frame_index: int = 0
        
        # Stepping state
        self.step_mode: Optional[str] = None  # 'step', 'next', 'return', 'until'
        self.step_frame: Optional[FrameType] = None
        self.step_depth: int = 0
        self.current_depth: int = 0
        
        # Setup readline for command history
        self._setup_readline()
        
        self.logger.info("GEAI debugger started.")
        self.logger.debug(f"Module filter: {self.module_filter}")

    def _setup_logging(self):
        """Setup logging configuration, avoiding duplicate handlers."""
        logger = logging.getLogger('geai.dbg')
        
        # Only setup if not already configured
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            logger.propagate = False

    def _setup_readline(self):
        """Setup readline for command history and tab completion."""
        try:
            import os
            histfile = os.path.expanduser("~/.geai_dbg_history")
            try:
                readline.read_history_file(histfile)
                readline.set_history_length(1000)
            except FileNotFoundError:
                pass
            
            import atexit
            atexit.register(readline.write_history_file, histfile)
        except Exception as e:
            self.logger.debug(f"Could not setup readline: {e}")

    def reset(self):
        """Reset debugger state."""
        self.breakpoints.clear()
        self.paused = False
        self.current_frame = None
        self.frame_stack.clear()
        self.current_frame_index = 0
        self.step_mode = None
        self.step_frame = None
        self.step_depth = 0
        self.current_depth = 0
        self.logger.info("Debugger state reset.")

    def add_breakpoint(
        self, 
        module: Optional[str] = None, 
        function_name: Optional[str] = None,
        condition: Optional[str] = None
    ) -> Breakpoint:
        """
        Add a breakpoint by module and/or function name.
        
        Args:
            module: Module name to break on (None for any)
            function_name: Function name to break on (None for any)
            condition: Optional condition expression (Python code)
            
        Returns:
            The created Breakpoint object
        """
        key = (module, function_name)
        if key in self.breakpoints:
            bp = self.breakpoints[key]
            self.logger.warning(f"Breakpoint already exists: {bp}")
            return bp
        
        bp = Breakpoint(module=module, function_name=function_name, condition=condition)
        self.breakpoints[key] = bp
        self.logger.info(f"Breakpoint added: {bp}")
        return bp

    def remove_breakpoint(self, module: Optional[str] = None, function_name: Optional[str] = None) -> bool:
        """Remove a breakpoint."""
        key = (module, function_name)
        if key in self.breakpoints:
            bp = self.breakpoints.pop(key)
            self.logger.info(f"Breakpoint removed: {bp}")
            return True
        self.logger.warning(f"Breakpoint not found: {module or '*'}:{function_name or '*'}")
        return False

    def list_breakpoints(self) -> List[Breakpoint]:
        """List all breakpoints."""
        return list(self.breakpoints.values())

    def enable_breakpoint(self, module: Optional[str] = None, function_name: Optional[str] = None) -> bool:
        """Enable a breakpoint."""
        key = (module, function_name)
        if key in self.breakpoints:
            self.breakpoints[key].enabled = True
            self.logger.info(f"Breakpoint enabled: {self.breakpoints[key]}")
            return True
        return False

    def disable_breakpoint(self, module: Optional[str] = None, function_name: Optional[str] = None) -> bool:
        """Disable a breakpoint."""
        key = (module, function_name)
        if key in self.breakpoints:
            self.breakpoints[key].enabled = False
            self.logger.info(f"Breakpoint disabled: {self.breakpoints[key]}")
            return True
        return False

    def clear_breakpoints(self):
        """Clear all breakpoints."""
        count = len(self.breakpoints)
        self.breakpoints.clear()
        self.logger.info(f"Cleared {count} breakpoint(s).")

    def _should_trace_module(self, module: Optional[str]) -> bool:
        """Check if we should trace this module based on filter."""
        if not module:
            return False
        return module.startswith(self.module_filter)

    def _check_condition(self, bp: Breakpoint, frame: FrameType) -> bool:
        """Check if breakpoint condition is met."""
        if not bp.condition:
            return True
        
        try:
            # Evaluate condition in frame's context
            result = eval(bp.condition, frame.f_globals, frame.f_locals)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error evaluating breakpoint condition '{bp.condition}': {e}")
            return False

    def _build_frame_stack(self, frame: FrameType) -> List[FrameType]:
        """Build a list of frames from current to top of stack."""
        stack = []
        current = frame
        while current is not None:
            stack.append(current)
            current = current.f_back
        return stack

    def trace_function(self, frame: FrameType, event: str, arg: Any) -> Optional[Callable]:
        """Trace function calls to intercept execution."""
        module = frame.f_globals.get('__name__')
        
        # Performance optimization: only trace filtered modules
        if not self._should_trace_module(module):
            return None
        
        function_name = frame.f_code.co_name
        
        # Handle different event types
        if event == 'call':
            self.current_depth += 1
            
            # Check breakpoints
            should_break = False
            for bp in self.breakpoints.values():
                if bp.matches(module, function_name):
                    if self._check_condition(bp, frame):
                        bp.hit_count += 1
                        self.logger.info(f"Breakpoint hit at {module}.{function_name} (hit #{bp.hit_count})")
                        should_break = True
                        break
            
            if should_break:
                self.paused = True
                self.current_frame = frame
                self.frame_stack = self._build_frame_stack(frame)
                self.current_frame_index = 0
                self.handle_breakpoint(frame)
                self.paused = False
        
        elif event == 'return':
            self.current_depth -= 1
            
            # Handle step-out (return from function)
            if self.step_mode == 'return' and frame == self.step_frame:
                self.step_mode = None
                self.paused = True
                self.current_frame = frame
                self.frame_stack = self._build_frame_stack(frame)
                self.current_frame_index = 0
                self.handle_breakpoint(frame)
                self.paused = False
        
        elif event == 'line':
            # Handle step and next
            if self.step_mode == 'step':
                self.step_mode = None
                self.paused = True
                self.current_frame = frame
                self.frame_stack = self._build_frame_stack(frame)
                self.current_frame_index = 0
                self.handle_breakpoint(frame)
                self.paused = False
            elif self.step_mode == 'next' and self.current_depth <= self.step_depth:
                self.step_mode = None
                self.paused = True
                self.current_frame = frame
                self.frame_stack = self._build_frame_stack(frame)
                self.current_frame_index = 0
                self.handle_breakpoint(frame)
                self.paused = False
        
        return self.trace_function

    def _get_source_lines(self, frame: FrameType, context: int = 5) -> Optional[List[Tuple[int, str]]]:
        """Get source code lines around the current line."""
        try:
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            start = max(0, lineno - context - 1)
            end = min(len(lines), lineno + context)
            
            return [(i + 1, lines[i].rstrip()) for i in range(start, end)]
        except Exception as e:
            self.logger.debug(f"Could not get source: {e}")
            return None

    def _print_source(self, frame: FrameType, context: int = 5):
        """Print source code around current line."""
        lines = self._get_source_lines(frame, context)
        if not lines:
            Console.write_stdout("Source code not available.")
            return
        
        lineno = frame.f_lineno
        Console.write_stdout(f"\nSource ({frame.f_code.co_filename}):")
        for num, line in lines:
            marker = "-> " if num == lineno else "   "
            Console.write_stdout(f"{marker}{num:4d}  {line}")

    def _print_stack_trace(self):
        """Print stack trace."""
        Console.write_stdout("\nStack trace (most recent call last):")
        for i, frame in enumerate(reversed(self.frame_stack)):
            marker = ">" if i == len(self.frame_stack) - 1 - self.current_frame_index else " "
            module = frame.f_globals.get('__name__', '?')
            func = frame.f_code.co_name
            lineno = frame.f_lineno
            filename = frame.f_code.co_filename
            Console.write_stdout(f"  {marker} #{i:2d} {module}.{func} at {filename}:{lineno}")

    def _move_frame(self, direction: int) -> bool:
        """Move up or down the frame stack."""
        new_index = self.current_frame_index + direction
        if 0 <= new_index < len(self.frame_stack):
            self.current_frame_index = new_index
            self.current_frame = self.frame_stack[new_index]
            Console.write_stdout(f"Frame #{len(self.frame_stack) - 1 - new_index}: "
                               f"{self.current_frame.f_globals.get('__name__', '?')}."
                               f"{self.current_frame.f_code.co_name}")
            return True
        else:
            Console.write_stdout(f"Cannot move {direction} (at {'top' if direction < 0 else 'bottom'} of stack)")
            return False

    def handle_breakpoint(self, frame: FrameType):
        """Handle a breakpoint by prompting for interactive commands."""
        module = frame.f_globals.get('__name__')
        func = frame.f_code.co_name
        
        Console.write_stdout(f"\n{'='*60}")
        Console.write_stdout(f"Paused at {module}.{func} (line {frame.f_lineno})")
        self._print_source(frame, context=3)
        Console.write_stdout(f"{'='*60}")
        Console.write_stdout("Type 'h' for help, 'c' to continue")
        
        while True:
            try:
                command = input("(geai-dbg) ").strip()
                if not command:
                    continue
                
                parts = command.split(None, 1)
                cmd = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                
                # Control flow commands
                if cmd in ('continue', 'c'):
                    break
                elif cmd in ('quit', 'q'):
                    self.logger.info("Debugger terminated by user.")
                    sys.exit(0)
                elif cmd in ('run', 'r'):
                    self.logger.info("Running program without further pauses.")
                    sys.settrace(None)
                    break
                
                # Stepping commands
                elif cmd in ('step', 's'):
                    self.step_mode = 'step'
                    self.step_depth = self.current_depth
                    break
                elif cmd in ('next', 'n'):
                    self.step_mode = 'next'
                    self.step_depth = self.current_depth
                    break
                elif cmd in ('return', 'ret'):
                    self.step_mode = 'return'
                    self.step_frame = frame
                    break
                
                # Stack navigation
                elif cmd in ('up', 'u'):
                    self._move_frame(1)
                elif cmd in ('down', 'd'):
                    self._move_frame(-1)
                elif cmd in ('where', 'w', 'bt', 'backtrace'):
                    self._print_stack_trace()
                
                # Source display
                elif cmd in ('list', 'l'):
                    context = int(args) if args.isdigit() else 10
                    self._print_source(self.current_frame, context)
                
                # Variable inspection
                elif cmd in ('print', 'p'):
                    if not args:
                        Console.write_stdout("Usage: p <expression>")
                    else:
                        try:
                            result = eval(args, self.current_frame.f_globals, self.current_frame.f_locals)
                            Console.write_stdout(repr(result))
                        except Exception as e:
                            Console.write_stdout(f"Error: {e}")
                
                elif cmd in ('pp',):
                    if not args:
                        Console.write_stdout("Usage: pp <expression>")
                    else:
                        try:
                            result = eval(args, self.current_frame.f_globals, self.current_frame.f_locals)
                            pprint.pprint(result)
                        except Exception as e:
                            Console.write_stdout(f"Error: {e}")
                
                elif cmd in ('locals', 'loc'):
                    Console.write_stdout("\nLocal variables:")
                    pprint.pprint(dict(self.current_frame.f_locals))
                
                elif cmd in ('globals', 'glob'):
                    Console.write_stdout("\nGlobal variables:")
                    # Filter out builtins
                    filtered = {k: v for k, v in self.current_frame.f_globals.items() 
                              if not k.startswith('__')}
                    pprint.pprint(filtered)
                
                elif cmd in ('args', 'a'):
                    Console.write_stdout("\nFunction arguments:")
                    arginfo = inspect.getargvalues(self.current_frame)
                    for arg in arginfo.args:
                        Console.write_stdout(f"  {arg} = {repr(self.current_frame.f_locals.get(arg))}")
                
                # Breakpoint management
                elif cmd in ('break', 'b'):
                    if not args:
                        # List breakpoints
                        bps = self.list_breakpoints()
                        if bps:
                            Console.write_stdout("\nBreakpoints:")
                            for i, bp in enumerate(bps, 1):
                                Console.write_stdout(f"  {i}. {bp}")
                        else:
                            Console.write_stdout("No breakpoints set.")
                    else:
                        # Parse breakpoint specification: module:function or just function
                        if ':' in args:
                            mod, func = args.split(':', 1)
                            mod = mod.strip() or None
                            func = func.strip() or None
                        else:
                            mod = None
                            func = args.strip()
                        self.add_breakpoint(module=mod, function_name=func)
                
                elif cmd in ('tbreak', 'tb'):
                    Console.write_stdout("Temporary breakpoints not yet implemented.")
                
                elif cmd in ('clear', 'cl'):
                    if args:
                        if ':' in args:
                            mod, func = args.split(':', 1)
                            mod = mod.strip() or None
                            func = func.strip() or None
                        else:
                            mod = None
                            func = args.strip()
                        self.remove_breakpoint(module=mod, function_name=func)
                    else:
                        Console.write_stdout("Usage: cl <breakpoint> or 'clearall' to remove all")
                
                elif cmd in ('clearall', 'cla'):
                    self.clear_breakpoints()
                
                elif cmd in ('enable', 'en'):
                    if ':' in args:
                        mod, func = args.split(':', 1)
                        mod = mod.strip() or None
                        func = func.strip() or None
                    else:
                        mod = None
                        func = args.strip()
                    self.enable_breakpoint(module=mod, function_name=func)
                
                elif cmd in ('disable', 'dis'):
                    if ':' in args:
                        mod, func = args.split(':', 1)
                        mod = mod.strip() or None
                        func = func.strip() or None
                    else:
                        mod = None
                        func = args.strip()
                    self.disable_breakpoint(module=mod, function_name=func)
                
                # Legacy commands
                elif cmd in ('breakpoint-module', 'bm'):
                    self.logger.info("Adding breakpoint on module")
                    module_name = input("(geai-dbg) Enter module name (or press Enter for any module): ").strip()
                    module_name = module_name if module_name else None
                    self.add_breakpoint(module=module_name)
                
                elif cmd in ('breakpoint-function', 'bf'):
                    self.logger.info("Adding breakpoint on function name")
                    function_name = input("(geai-dbg) Enter function name (or press Enter for any function): ").strip()
                    function_name = function_name if function_name else None
                    module_name = input("(geai-dbg) Enter module name (optional, press Enter to skip): ").strip()
                    module_name = module_name if module_name else None
                    self.add_breakpoint(module=module_name, function_name=function_name)
                
                elif cmd in ('list-modules', 'lm'):
                    self.logger.info("Listing available modules")
                    modules = [m for m in sys.modules if m.startswith(self.module_filter)]
                    Console.write_stdout(f"\nAvailable modules ({len(modules)}):")
                    for mod in sorted(modules)[:50]:  # Limit output
                        Console.write_stdout(f"  {mod}")
                    if len(modules) > 50:
                        Console.write_stdout(f"  ... and {len(modules) - 50} more")
                
                # Help
                elif cmd in ('help', 'h', '?'):
                    self._print_help()
                
                # Execute arbitrary Python code
                else:
                    self.logger.info(f"Executing interactive command: {command}")
                    try:
                        # Try exec first, if it fails try eval and print result
                        try:
                            exec(command, self.current_frame.f_globals, self.current_frame.f_locals)
                        except SyntaxError:
                            result = eval(command, self.current_frame.f_globals, self.current_frame.f_locals)
                            Console.write_stdout(repr(result))
                    except Exception as e:
                        self.logger.error(f"Command execution failed: {e}")
                        Console.write_stdout(f"Error: {e}")
            
            except EOFError:
                self.logger.info("Debugger terminated by user (EOF).")
                sys.exit(0)
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received. Continuing execution.")
                break

    def _print_help(self):
        """Print help message."""
        help_text = """
Available commands:

Flow Control:
  continue, c          Resume execution until next breakpoint
  step, s              Step into function calls
  next, n              Step over function calls (same level)
  return, ret          Continue until current function returns
  run, r               Run program to completion (disable tracing)
  quit, q              Exit the debugger

Stack Navigation:
  where, w, bt         Show stack trace
  up, u                Move up one stack frame
  down, d              Move down one stack frame

Source Display:
  list, l [n]          Show source code (n lines of context, default 10)

Variable Inspection:
  print, p <expr>      Evaluate and print expression
  pp <expr>            Pretty-print expression
  locals, loc          Show local variables
  globals, glob        Show global variables
  args, a              Show function arguments

Breakpoints:
  break, b             List all breakpoints
  b <func>             Set breakpoint on function
  b <module>:<func>    Set breakpoint on module:function
  clear, cl <bp>       Remove breakpoint
  clearall, cla        Remove all breakpoints
  enable, en <bp>      Enable breakpoint
  disable, dis <bp>    Disable breakpoint

Legacy Commands:
  breakpoint-module, bm    Add module breakpoint (interactive)
  breakpoint-function, bf  Add function breakpoint (interactive)
  list-modules, lm         List available modules

Other:
  help, h, ?           Show this help
  <Python code>        Execute arbitrary Python code

Examples:
  p sys.argv           Print command-line arguments
  b main               Set breakpoint on any 'main' function
  b pygeai.cli:main    Set breakpoint on pygeai.cli.main
  pp locals()          Pretty-print all local variables
"""
        Console.write_stdout(help_text)

    def run(self):
        """Run the target callable under the debugger."""
        self.logger.info("Setting trace and running target")
        sys.settrace(self.trace_function)
        try:
            self.target()
        except Exception as e:
            self.logger.error(f"Target execution failed: {e}")
            raise
        finally:
            self.logger.info("Cleaning up trace")
            sys.settrace(None)


def main():
    """Entry point for geai-dbg command."""
    dbg = Debugger()
    dbg.add_breakpoint(module='pygeai.cli.geai', function_name='main')
    dbg.run()


if __name__ == "__main__":
    main()
