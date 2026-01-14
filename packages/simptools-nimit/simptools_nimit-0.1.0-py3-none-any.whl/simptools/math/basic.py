def add(a, b):
    if a is None or b is None:
        raise ValueError("Both operands must be provided")
    return a + b

def subtract(a, b):
    if a is None or b is None:
        raise ValueError("Both operands must be provided")
    return a - b

def multiply(a, b):
    if a is None or b is None:
        raise ValueError("Both operands must be provided")
    return a * b

def divide(a, b):
    if a is None or b is None:
        raise ValueError("Both operands must be provided")
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def clamp(value, min_val, max_val):
    if min_val > max_val:
        raise ValueError("min_val cannot be greater than max_val")
    return max(min_val, min(value, max_val))

def power(a, b):
    if a is None or b is None:
        raise ValueError("Both operands must be provided")
    return a ** b
