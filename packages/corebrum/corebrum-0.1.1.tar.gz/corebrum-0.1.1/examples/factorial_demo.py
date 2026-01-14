"""
Factorial Demo - Demonstrates using Corebrum Python library to compute factorials.

This demo shows the difference between corebrum.run() and corebrum.execute():

Method 1: @corebrum.run() decorator
- Best for: Existing functions you want to run remotely
- Automatically extracts function arguments
- Minimal code changes (just add decorator)
- Uses function's return value as result

Method 2: corebrum.execute()
- Best for: Raw code strings, dynamic code generation
- Requires explicit input_data dictionary
- Must assign result to a variable (result, output, data, etc.)
- More flexible for ad-hoc code

This demo mimics the command:
    corebrum submit --file https://gist.github.com/chrismatthieu/e06cdd5c6c3787d7e68e2c6977d81e9e --input '{"number": 8}'

But uses the Corebrum Python library instead of the CLI.
"""

import corebrum
import json


# Configure Corebrum connection
corebrum.configure(
    base_url="http://localhost:6502",
    # identity_id="your-identity-id"  # Optional
)


# Method 1: Using the @run() decorator
# 
# BEST FOR: Existing functions you want to run remotely
# - Automatically extracts function arguments from the call
# - Uses function's return value as result
# - Minimal code changes (just add decorator)
#
@corebrum.run()
def factorial(number):
    """
    Calculate factorial of a number.
    
    This function will execute on Corebrum's distributed infrastructure.
    Arguments are automatically extracted when you call factorial(8).
    Similar to the gist implementation at:
    https://gist.github.com/chrismatthieu/e06cdd5c6c3787d7e68e2c6977d81e9e
    """
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    if number == 0 or number == 1:
        return 1
    
    result = 1
    for i in range(2, number + 1):
        result *= i
    
    return result


# Method 2: Using execute() with code similar to the gist
#
# BEST FOR: Raw code strings, dynamic code generation
# - Requires explicit input_data dictionary
# - Must assign result to a variable (result, output, data, etc.)
# - More flexible for ad-hoc code or code that isn't in a function
#
def factorial_execute(number):
    """
    Calculate factorial using execute() method.
    
    This demonstrates executing code directly, similar to submitting
    a file URL to Corebrum.
    
    Note: The code must assign the result to a variable (e.g., 'result')
    for execute() to capture it. execute() looks for common variable names:
    result, output, data, value, answer, res
    """
    code = """
def factorial(number):
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    if number == 0 or number == 1:
        return 1
    
    result = 1
    for i in range(2, number + 1):
        result *= i
    
    return result

# Call the function and assign result
result = factorial(number)
"""
    
    result = corebrum.execute(
        code,
        input_data={"number": number},
        name="factorial_task"
    )
    
    return result


# Method 3: Recursive factorial (alternative implementation)
# 
# This shows that @run() works with recursive functions too.
# The decorator handles the function call automatically.
#
@corebrum.run()
def factorial_recursive(number):
    """
    Calculate factorial using recursion.
    
    Note: Recursive calls work normally - the decorator only intercepts
    the initial call, not internal recursive calls.
    """
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    if number == 0 or number == 1:
        return 1
    
    return number * factorial_recursive(number - 1)


def main():
    """Run factorial demos."""
    print("=" * 60)
    print("Corebrum Factorial Demo")
    print("=" * 60)
    print()
    
    # Test with number 8 (matching the original command)
    test_number = 8
    
    print(f"Calculating factorial of {test_number}...")
    print()
    
    # Method 1: Decorator pattern
    print("Method 1: Using @corebrum.run() decorator")
    print("-" * 60)
    try:
        result1 = factorial(test_number)
        print(f"✅ Factorial({test_number}) = {result1}")
        print(f"   Expected: 40320")
        print(f"   Match: {'✓' if result1 == 40320 else '✗'}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Method 2: Execute method
    print("Method 2: Using corebrum.execute()")
    print("-" * 60)
    try:
        result2 = factorial_execute(test_number)
        # Result might be wrapped in a dict, extract it
        if isinstance(result2, dict):
            result2 = result2.get("result", result2)
        print(f"✅ Factorial({test_number}) = {result2}")
        print(f"   Expected: 40320")
        print(f"   Match: {'✓' if result2 == 40320 else '✗'}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Method 3: Recursive version
    print("Method 3: Recursive factorial")
    print("-" * 60)
    try:
        result3 = factorial_recursive(test_number)
        print(f"✅ Factorial({test_number}) = {result3}")
        print(f"   Expected: 40320")
        print(f"   Match: {'✓' if result3 == 40320 else '✗'}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test with multiple numbers
    print("Testing with multiple numbers:")
    print("-" * 60)
    test_numbers = [0, 1, 5, 8, 10]
    
    for num in test_numbers:
        try:
            result = factorial(num)
            # Handle case where result might be a dict or wrapped
            if isinstance(result, dict):
                result = result.get("result", result.get("value", result))
            # Convert to int if it's a string representation of a number
            if isinstance(result, str) and result.isdigit():
                result = int(result)
            expected = 1 if num == 0 else (1 if num == 1 else 
                (120 if num == 5 else (40320 if num == 8 else 3628800)))
            # Format result safely - handle both int and dict cases
            if isinstance(result, (int, float)):
                print(f"  Factorial({num:2d}) = {result:10d} {'✓' if result == expected else '✗'}")
            else:
                print(f"  Factorial({num:2d}) = {result} {'✓' if result == expected else '✗'}")
        except Exception as e:
            print(f"  Factorial({num:2d}) = Error: {e}")
    
    print()
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

