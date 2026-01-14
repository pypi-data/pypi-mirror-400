"""
Demonstrates stepping functionality (step, next, return).
"""
from pygeai.dbg.debugger import Debugger


def helper_function(n):
    """Helper function to demonstrate step-into."""
    doubled = n * 2
    return doubled


def process_data(data):
    """Process some data."""
    result = []
    for item in data:
        processed = helper_function(item)
        result.append(processed)
    return result


def main():
    """Main entry point."""
    numbers = [1, 2, 3, 4, 5]
    processed = process_data(numbers)
    print(f"Processed: {processed}")


if __name__ == "__main__":
    dbg = Debugger(target=main, module_filter="__main__")
    dbg.add_breakpoint(module="__main__", function_name="process_data")
    
    print("Starting debugger...")
    print("At breakpoint, try:")
    print("  's' - step into helper_function")
    print("  'n' - step over helper_function call")
    print("  'ret' - return from current function")
    print("  'l' - list source code")
    
    dbg.run()
