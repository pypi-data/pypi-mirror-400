"""
Demonstrates breakpoint management (add, list, remove, enable/disable).
"""
from pygeai.dbg.debugger import Debugger


def func_a():
    """Function A."""
    print("In function A")
    return "A"


def func_b():
    """Function B."""
    print("In function B")
    return "B"


def func_c():
    """Function C."""
    print("In function C")
    return "C"


def main():
    """Main entry point."""
    results = []
    results.append(func_a())
    results.append(func_b())
    results.append(func_c())
    print(f"Results: {results}")


if __name__ == "__main__":
    dbg = Debugger(target=main, module_filter="__main__")
    
    print("Starting debugger...")
    print("No breakpoints set initially. At first function, try:")
    print("  'b func_b' - add breakpoint on func_b")
    print("  'b __main__:func_c' - add breakpoint on specific module:function")
    print("  'b' - list all breakpoints")
    print("  'dis func_b' - disable breakpoint on func_b")
    print("  'en func_b' - enable breakpoint on func_b")
    print("  'cl func_b' - remove breakpoint on func_b")
    print("  'c' - continue to next breakpoint")
    
    dbg.add_breakpoint(module="__main__", function_name="func_a")
    dbg.run()
