PyGEAI Debugger
===============

Overview
--------

``geai-dbg`` is a command-line debugger for the ``geai`` CLI tool, part of the ``pygeai`` package. It allows developers to pause execution at specified points (breakpoints) in the ``geai`` codebase, inspect local variables, navigate the call stack, step through code execution, and control program flow interactively.

The debugger provides features similar to Python's built-in ``pdb`` debugger, including:

- **Breakpoint management**: Set, list, enable/disable, and remove breakpoints
- **Stepping**: Step into, over, and out of function calls
- **Stack navigation**: Move up and down the call stack to inspect different frames
- **Variable inspection**: Print, pretty-print, and examine local/global variables
- **Source code display**: View source code around the current execution point
- **Performance optimization**: Only traces relevant modules to minimize overhead
- **Command history**: Uses readline for command history and editing

Installation and Setup
---------------------

``geai-dbg`` is included in the ``pygeai`` package. Ensure ``pygeai`` is installed in your Python environment:

.. code-block:: bash

    pip install pygeai

No additional setup is required. The debugger script (``debugger.py``) is located in the ``pygeai.dbg`` module and can be invoked via the ``geai-dbg`` command.

Usage
-----

Basic Usage
~~~~~~~~~~~

To use ``geai-dbg``, run it with the same arguments you would pass to the ``geai`` CLI. For example:

.. code-block:: bash

    geai-dbg ail lrs

This command runs the ``geai`` CLI with the arguments ``ail lrs`` under the debugger. The debugger automatically sets a breakpoint at the ``main`` function in the ``pygeai.cli.geai`` module, pausing execution before the ``geai`` command processes the arguments.

Upon hitting a breakpoint, the debugger displays:

- The location (module and function) where execution is paused
- Source code context around the current line
- An interactive prompt ``(geai-dbg)`` for entering commands

Custom Target Functions
~~~~~~~~~~~~~~~~~~~~~~~

You can also debug custom Python functions using the ``Debugger`` class directly:

.. code-block:: python

    from pygeai.dbg.debugger import Debugger
    
    def my_function():
        x = 10
        y = 20
        result = x + y
        print(f"Result: {result}")
    
    # Create debugger and set breakpoint
    dbg = Debugger(target=my_function, module_filter="__main__")
    dbg.add_breakpoint(module="__main__", function_name="my_function")
    dbg.run()

Commands Reference
------------------

At the ``(geai-dbg)`` prompt, the following commands are available:

Flow Control
~~~~~~~~~~~~

**continue, c**
    Resume execution until the next breakpoint is hit or the program completes.

**step, s**
    Execute the current line and stop at the first possible occasion (either in a function that is called or on the next line in the current function).

**next, n**
    Continue execution until the next line in the current function is reached or it returns (step over function calls).

**return, ret**
    Continue execution until the current function returns.

**run, r**
    Run the program to completion, disabling all breakpoints and skipping further pauses.

**quit, q, Ctrl+D**
    Exit the debugger, terminating the program with a clean exit status (0).

Stack Navigation
~~~~~~~~~~~~~~~~

**where, w, bt, backtrace**
    Display the stack trace, showing all frames from the current execution point to the top of the call stack.

**up, u**
    Move up one level in the stack trace (to an older frame). This allows you to inspect the context of the caller.

**down, d**
    Move down one level in the stack trace (to a newer frame).

Source Display
~~~~~~~~~~~~~~

**list, l [n]**
    Show source code around the current line. Optional argument ``n`` specifies the number of lines of context (default: 10).

Variable Inspection
~~~~~~~~~~~~~~~~~~~

**print, p <expression>**
    Evaluate and print the value of a Python expression in the current frame's context.
    
    Example: ``p x + y``

**pp <expression>**
    Pretty-print the value of a Python expression using ``pprint.pprint()``.
    
    Example: ``pp locals()``

**locals, loc**
    Display all local variables in the current frame.

**globals, glob**
    Display all global variables in the current frame (excluding built-ins).

**args, a**
    Display the arguments of the current function.

Breakpoint Management
~~~~~~~~~~~~~~~~~~~~~

**break, b**
    List all breakpoints with their status, hit counts, and conditions.

**b <function>**
    Set a breakpoint on any function with the given name.
    
    Example: ``b main``

**b <module>:<function>**
    Set a breakpoint on a specific function in a specific module.
    
    Example: ``b pygeai.cli.geai:main``

**clear, cl <breakpoint>**
    Remove a breakpoint. Use the same syntax as setting a breakpoint.
    
    Example: ``cl main`` or ``cl pygeai.cli.geai:main``

**clearall, cla**
    Remove all breakpoints.

**enable, en <breakpoint>**
    Enable a disabled breakpoint.
    
    Example: ``en main``

**disable, dis <breakpoint>**
    Disable a breakpoint without removing it.
    
    Example: ``dis main``

Legacy Commands
~~~~~~~~~~~~~~~

These commands are maintained for backward compatibility:

**breakpoint-module, bm**
    Add a breakpoint for a specific module (interactive prompt).

**breakpoint-function, bf**
    Add a breakpoint for a specific function (interactive prompt).

**list-modules, lm**
    List all loaded modules starting with the module filter (default: ``pygeai``).

Other Commands
~~~~~~~~~~~~~~

**help, h, ?**
    Display a list of available commands and their descriptions.

**<Python code>**
    Execute arbitrary Python code in the current frame's context. For example, ``x = 42`` or ``print(sys.argv)``. Errors are caught and logged without crashing the debugger.

**Ctrl+C**
    Interrupt the current command input and resume execution, equivalent to ``continue``.

Examples
--------

Example 1: Basic Debugging
~~~~~~~~~~~~~~~~~~~~~~~~~~

Debug the ``geai ail lrs`` command:

.. code-block:: bash

    geai-dbg ail lrs

Output:

.. code-block:: text

    2026-01-07 15:04:57,263 - geai.dbg - INFO - GEAI debugger started.
    2026-01-07 15:04:57,264 - geai.dbg - INFO - Breakpoint added: pygeai.cli.geai:main (enabled, hits: 0)
    2026-01-07 15:04:57,264 - geai.dbg - INFO - Setting trace and running target
    2026-01-07 15:04:57,264 - geai.dbg - INFO - Breakpoint hit at pygeai.cli.geai.main (hit #1)
    
    ============================================================
    Paused at pygeai.cli.geai.main (line 42)
    
    Source (/path/to/pygeai/cli/geai.py):
       39  
       40  class CLIDriver:
       41      def main(self):
    -> 42          parser = ArgumentParser()
       43          args = parser.parse_args()
       44          return self.execute(args)
       45  
    ============================================================
    Type 'h' for help, 'c' to continue
    (geai-dbg)

Example 2: Stepping Through Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At a breakpoint, step through code execution:

.. code-block:: text

    (geai-dbg) s
    # Steps into the next function call
    
    (geai-dbg) n
    # Steps over function calls, staying in the current function
    
    (geai-dbg) ret
    # Continues until the current function returns

Example 3: Inspecting Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examine variables at a breakpoint:

.. code-block:: text

    (geai-dbg) p x
    42
    
    (geai-dbg) pp locals()
    {'x': 42,
     'y': 20,
     'result': 62}
    
    (geai-dbg) args
    Function arguments:
      self = <pygeai.cli.geai.CLIDriver object at 0x...>
      args = None

Example 4: Stack Navigation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Navigate the call stack:

.. code-block:: text

    (geai-dbg) where
    Stack trace (most recent call last):
       #0  __main__.level_3 at /path/to/script.py:15
      > #1  __main__.level_2 at /path/to/script.py:10
       #2  __main__.level_1 at /path/to/script.py:5
    
    (geai-dbg) up
    Frame #0: __main__.level_2
    
    (geai-dbg) locals
    Local variables:
    {'value': 'level 2'}
    
    (geai-dbg) down
    Frame #1: __main__.level_3

Example 5: Breakpoint Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manage breakpoints during debugging:

.. code-block:: text

    (geai-dbg) b
    Breakpoints:
      1. pygeai.cli.geai:main (enabled, hits: 1)
    
    (geai-dbg) b process_data
    Breakpoint added: *:process_data (enabled, hits: 0)
    
    (geai-dbg) b pygeai.core:helper_function
    Breakpoint added: pygeai.core:helper_function (enabled, hits: 0)
    
    (geai-dbg) dis process_data
    Breakpoint disabled: *:process_data (disabled, hits: 0)
    
    (geai-dbg) cl pygeai.core:helper_function
    Breakpoint removed: pygeai.core:helper_function

Example 6: Viewing Source Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display source code around the current line:

.. code-block:: text

    (geai-dbg) list 5
    Source (/path/to/file.py):
       10  def process_data(data):
       11      result = []
       12      for item in data:
    ->  13          processed = helper_function(item)
       14          result.append(processed)
       15      return result

Advanced Features
-----------------

Module Filtering
~~~~~~~~~~~~~~~~

The debugger includes a performance optimization that only traces modules matching a specified prefix (default: ``pygeai``). This significantly reduces overhead compared to tracing all Python code.

When creating a custom debugger, you can specify the module filter:

.. code-block:: python

    dbg = Debugger(target=my_function, module_filter="my_package")

This will only trace modules starting with ``my_package``, ignoring standard library and third-party code.

Conditional Breakpoints
~~~~~~~~~~~~~~~~~~~~~~~

Breakpoints can include conditions that must be met for the breakpoint to trigger:

.. code-block:: python

    dbg = Debugger(target=my_function)
    dbg.add_breakpoint(
        module="my_module",
        function_name="process_item",
        condition="item > 100"
    )

The breakpoint will only trigger when ``item > 100`` evaluates to ``True`` in the function's context.

Command History
~~~~~~~~~~~~~~~

The debugger uses Python's ``readline`` module to provide command history and line editing. You can use:

- **Up/Down arrows**: Navigate through command history
- **Ctrl+R**: Search command history
- **Tab**: (if configured) Auto-completion

Command history is saved to ``~/.geai_dbg_history`` and persists across debugging sessions.

Programmatic Usage
~~~~~~~~~~~~~~~~~~

You can use the ``Debugger`` class programmatically in your own code:

.. code-block:: python

    from pygeai.dbg.debugger import Debugger, Breakpoint
    
    def my_target():
        # Your code here
        pass
    
    # Create debugger
    dbg = Debugger(target=my_target, module_filter="my_package")
    
    # Add breakpoints
    dbg.add_breakpoint(module="my_package.module", function_name="my_function")
    dbg.add_breakpoint(function_name="helper", condition="x > 10")
    
    # List breakpoints
    for bp in dbg.list_breakpoints():
        print(f"Breakpoint: {bp}")
    
    # Run under debugger
    dbg.run()
    
    # Reset state for reuse
    dbg.reset()

Tips and Best Practices
-----------------------

1. **Start with targeted breakpoints**: Set specific breakpoints on the functions you want to debug rather than using wildcards.

2. **Use step wisely**: The ``step`` command can be slow if it steps into many library functions. Use ``next`` to stay at the same level.

3. **Inspect the stack**: Use ``where`` to understand the call chain, especially in complex codebases.

4. **Pretty-print complex data**: Use ``pp`` instead of ``p`` for dictionaries, lists, and other complex structures.

5. **Disable instead of removing**: Use ``disable`` to temporarily turn off breakpoints you might need again, rather than removing them.

6. **Use module filtering**: When debugging custom code, set ``module_filter`` to your package name to avoid tracing unrelated code.

7. **Conditional breakpoints**: Use conditions to break only when specific criteria are met, reducing manual stepping.

Notes
-----

- **Ctrl+D and Ctrl+C**:
  - Pressing ``Ctrl+D`` at the ``(geai-dbg)`` prompt terminates the debugger gracefully, logging "Debugger terminated by user (EOF)." and exiting with status 0.
  - Pressing ``Ctrl+C`` resumes execution, equivalent to the ``continue`` command.

- **Python Code Execution**:
  - Arbitrary Python code executed at the prompt runs in the context of the current frame, with access to local and global variables. Use with caution, as it can modify program state.

- **Performance**:
  - The debugger uses ``sys.settrace`` which has performance overhead. The module filter helps minimize this, but expect slower execution than running without the debugger.

- **Breakpoint Persistence**:
  - Breakpoints persist across ``continue`` commands but are cleared when the program exits. They are not saved to disk.

- **Logging**:
  - The debugger logs to stdout with timestamps, including breakpoint hits, state changes, and errors. The log level is set to DEBUG by default.

- **Frame Context**:
  - When you move up/down the stack with ``up``/``down``, the current frame changes, affecting what ``locals``, ``globals``, and expression evaluation see.

Code Examples
-------------

See the ``pygeai/tests/snippets/dbg/`` directory for complete working examples:

- ``basic_debugging.py`` - Simple debugging with variable inspection
- ``stepping_example.py`` - Demonstrates step, next, and return commands
- ``stack_navigation.py`` - Shows stack traversal with up/down
- ``breakpoint_management.py`` - Examples of managing breakpoints

Run these examples with:

.. code-block:: bash

    python -m pygeai.tests.snippets.dbg.basic_debugging

Troubleshooting
---------------

**Debugger is too slow**
    Adjust the ``module_filter`` to trace only the modules you care about. The default filter is ``"pygeai"``.

**Breakpoint not hitting**
    - Check that the module and function names match exactly (use ``lm`` to list loaded modules)
    - Verify the breakpoint is enabled (use ``b`` to list breakpoints)
    - Check if a condition is preventing the breakpoint from triggering

**Can't see local variables**
    Make sure you're in the correct frame. Use ``where`` to see the stack and ``up``/``down`` to navigate.

**Source code not displaying**
    The source file might not be accessible or the code might be in a compiled module. The debugger needs access to the ``.py`` source files.

For issues or feature requests, contact the ``pygeai`` development team or file an issue on the project's GitHub repository.

.. seealso::

   - ``geai`` CLI documentation for details on the underlying command-line tool
   - Python's ``sys.settrace`` documentation for technical details on the debugging mechanism
   - Python's ``pdb`` module for comparison with the standard Python debugger
