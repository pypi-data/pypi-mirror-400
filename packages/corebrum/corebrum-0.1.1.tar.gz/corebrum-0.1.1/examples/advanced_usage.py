"""
Advanced usage examples for Corebrum Python library.
"""

import corebrum
from corebrum.exceptions import TaskExecutionError, TaskTimeoutError


# Example 1: Function with default arguments
@corebrum.run()
def process_with_defaults(data, multiplier=2, offset=0):
    """Process data with default arguments."""
    return [x * multiplier + offset for x in data]


# Example 2: Error handling
@corebrum.run()
def risky_operation(x):
    """Operation that might fail."""
    if x < 0:
        raise ValueError("Negative numbers not allowed")
    return x ** 2


# Example 3: Custom timeout
@corebrum.run(timeout=600)  # 10 minutes
def long_running_task():
    """Long running task with custom timeout."""
    import time
    time.sleep(5)  # Simulate work
    return "Task completed"


# Example 4: Using identity context
@corebrum.run(identity_id="my-identity-id")
def task_with_identity(data):
    """Task that uses identity context for memory."""
    # This task will have access to identity memory
    return {"processed": len(data)}


# Example 5: Execute with inputs
def example_execute_with_inputs():
    """Example using execute() with input data."""
    result = corebrum.execute(
        """
        def process(x, y):
            return x * y + 10
        
        # Must assign to a variable for execute() to capture it
        result = process(x, y)
        """,
        input_data={"x": 5, "y": 3}
    )
    return result


# Example 6: Error handling
def example_error_handling():
    """Example of error handling."""
    try:
        result = risky_operation(-5)
        print(f"Result: {result}")
    except TaskExecutionError as e:
        print(f"Task execution failed: {e}")
    except TaskTimeoutError as e:
        print(f"Task timed out: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("Example 1: Default arguments")
    result1 = process_with_defaults([1, 2, 3], multiplier=3, offset=1)
    print(f"Result: {result1}\n")
    
    print("Example 2: Error handling")
    example_error_handling()
    print()
    
    print("Example 3: Custom timeout")
    result3 = long_running_task()
    print(f"Result: {result3}\n")
    
    print("Example 5: Execute with inputs")
    result5 = example_execute_with_inputs()
    print(f"Result: {result5}\n")

