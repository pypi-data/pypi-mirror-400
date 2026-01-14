from typing import Literal


def greet(name: str) -> str:
    """
    Greet someone by name.
    
    Args:
        name: The name of the person to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! Welcome to SMF."


def calculate(operation: Literal["add", "subtract", "multiply", "divide"], a: float, b: float) -> float:
    """
    Perform a mathematical calculation.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
        
    Returns:
        The result of the calculation
        
    Raises:
        ValueError: If operation is invalid or division by zero
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")
