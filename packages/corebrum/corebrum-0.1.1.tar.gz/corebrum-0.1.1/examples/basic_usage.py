"""
Basic usage examples for Corebrum Python library.
"""

import corebrum

# Configure Corebrum connection
corebrum.configure(
    base_url="http://localhost:6502",
    # identity_id="your-identity-id"  # Optional
)


# Example 1: Simple function
@corebrum.run()
def add_numbers(a, b):
    """Add two numbers."""
    return a + b


# Example 2: Data processing with pandas
@corebrum.run()
def process_data(data):
    """Process data using pandas."""
    import pandas as pd
    
    df = pd.DataFrame(data)
    return {
        "mean": df.mean().to_dict(),
        "count": len(df)
    }


# Example 3: Mathematical computation
@corebrum.run()
def calculate_factorial(n):
    """Calculate factorial."""
    import math
    return math.factorial(n)


# Example 4: Using execute() method
def example_execute():
    """Example using execute() method."""
    result = corebrum.execute("""
        import math
        def calculate():
            return math.sqrt(144)
        # Must assign to a variable for execute() to capture it
        result = calculate()
    """)
    return result


if __name__ == "__main__":
    # Run examples
    print("Example 1: Adding numbers")
    result1 = add_numbers(5, 3)
    print(f"Result: {result1}\n")
    
    print("Example 2: Processing data")
    data = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
    result2 = process_data(data)
    print(f"Result: {result2}\n")
    
    print("Example 3: Factorial")
    result3 = calculate_factorial(5)
    print(f"Result: {result3}\n")
    
    print("Example 4: Execute method")
    result4 = example_execute()
    print(f"Result: {result4}\n")

