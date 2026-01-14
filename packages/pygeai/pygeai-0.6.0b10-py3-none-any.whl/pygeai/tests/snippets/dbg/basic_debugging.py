"""
Basic debugging example with geai-dbg.

This demonstrates setting breakpoints and inspecting variables.
"""
from pygeai.dbg.debugger import Debugger


def example_function(x, y):
    """A simple function to debug."""
    result = x + y
    print(f"Result: {result}")
    return result


def main():
    """Main entry point."""
    a = 10
    b = 20
    c = example_function(a, b)
    print(f"Final value: {c}")


if __name__ == "__main__":
    dbg = Debugger(target=main, module_filter="__main__")
    dbg.add_breakpoint(module="__main__", function_name="example_function")
    
    print("Starting debugger...")
    print("Type 'h' for help")
    print("Try commands like: 'p x', 'p y', 'locals', 's', 'n', 'c'")
    
    dbg.run()
