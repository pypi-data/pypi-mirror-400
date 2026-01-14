"""
Demonstrates stack navigation (up, down, where).
"""
from pygeai.dbg.debugger import Debugger


def level_3():
    """Deepest level of call stack."""
    value = "level 3"
    print(f"At {value}")
    return value


def level_2():
    """Middle level of call stack."""
    value = "level 2"
    result = level_3()
    return f"{value} -> {result}"


def level_1():
    """Top level of call stack."""
    value = "level 1"
    result = level_2()
    return f"{value} -> {result}"


def main():
    """Main entry point."""
    result = level_1()
    print(f"Final: {result}")


if __name__ == "__main__":
    dbg = Debugger(target=main, module_filter="__main__")
    dbg.add_breakpoint(module="__main__", function_name="level_3")
    
    print("Starting debugger...")
    print("At breakpoint in level_3, try:")
    print("  'where' or 'bt' - show call stack")
    print("  'up' - move to level_2 frame")
    print("  'down' - move back to level_3 frame")
    print("  'locals' - show local variables in current frame")
    
    dbg.run()
