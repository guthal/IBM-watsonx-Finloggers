"""
Math Tool - Basic arithmetic operations for financial calculations
Provides addition, subtraction, multiplication, division, percentage, and compound calculations
"""
from typing import Union, List
from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool()
def add(a: float, b: float) -> dict:
    """Add two numbers.

    Args:
        a (float): First number
        b (float): Second number

    Returns:
        dict: Result of a + b
    """
    result = a + b
    return {
        "operation": "addition",
        "expression": f"{a} + {b}",
        "result": result
    }


@tool()
def subtract(a: float, b: float) -> dict:
    """Subtract second number from first number.

    Args:
        a (float): First number (minuend)
        b (float): Second number (subtrahend)

    Returns:
        dict: Result of a - b
    """
    result = a - b
    return {
        "operation": "subtraction",
        "expression": f"{a} - {b}",
        "result": result
    }


@tool()
def multiply(a: float, b: float) -> dict:
    """Multiply two numbers.

    Args:
        a (float): First number
        b (float): Second number

    Returns:
        dict: Result of a × b
    """
    result = a * b
    return {
        "operation": "multiplication",
        "expression": f"{a} × {b}",
        "result": result
    }


@tool()
def divide(a: float, b: float) -> dict:
    """Divide first number by second number.

    Args:
        a (float): Numerator
        b (float): Denominator

    Returns:
        dict: Result of a ÷ b, or error if division by zero
    """
    if b == 0:
        return {
            "operation": "division",
            "expression": f"{a} ÷ {b}",
            "error": "Cannot divide by zero"
        }

    result = a / b
    return {
        "operation": "division",
        "expression": f"{a} ÷ {b}",
        "result": result
    }


@tool()
def percentage(value: float, percent: float) -> dict:
    """Calculate percentage of a value.

    Args:
        value (float): The base value
        percent (float): The percentage (e.g., 15 for 15%)

    Returns:
        dict: Result of (value × percent / 100)
    """
    result = (value * percent) / 100
    return {
        "operation": "percentage",
        "expression": f"{percent}% of {value}",
        "result": result,
        "formatted": f"{result:.2f}"
    }


@tool()
def percentage_change(old_value: float, new_value: float) -> dict:
    """Calculate percentage change between two values.

    Args:
        old_value (float): Original value
        new_value (float): New value

    Returns:
        dict: Percentage change ((new - old) / old × 100)
    """
    if old_value == 0:
        return {
            "operation": "percentage_change",
            "error": "Cannot calculate percentage change from zero"
        }

    change = new_value - old_value
    percent_change = (change / old_value) * 100

    return {
        "operation": "percentage_change",
        "old_value": old_value,
        "new_value": new_value,
        "absolute_change": change,
        "percentage_change": percent_change,
        "formatted": f"{percent_change:+.2f}%",
        "direction": "increase" if percent_change > 0 else "decrease" if percent_change < 0 else "no change"
    }


@tool()
def average(numbers: List[float]) -> dict:
    """Calculate the average (mean) of a list of numbers.

    Args:
        numbers (List[float]): List of numbers to average

    Returns:
        dict: Average of the numbers
    """
    if not numbers:
        return {
            "operation": "average",
            "error": "Cannot calculate average of empty list"
        }

    total = sum(numbers)
    count = len(numbers)
    avg = total / count

    return {
        "operation": "average",
        "numbers": numbers,
        "count": count,
        "sum": total,
        "average": avg,
        "formatted": f"{avg:.2f}"
    }


@tool()
def compound_growth(principal: float, rate: float, periods: int) -> dict:
    """Calculate compound growth (compound interest formula).

    Args:
        principal (float): Initial value
        rate (float): Growth rate per period as percentage (e.g., 5 for 5%)
        periods (int): Number of periods

    Returns:
        dict: Final value using A = P(1 + r)^n
    """
    if periods < 0:
        return {
            "operation": "compound_growth",
            "error": "Number of periods must be non-negative"
        }

    rate_decimal = rate / 100
    final_value = principal * ((1 + rate_decimal) ** periods)
    total_growth = final_value - principal
    total_growth_percent = (total_growth / principal) * 100

    return {
        "operation": "compound_growth",
        "principal": principal,
        "rate_percent": rate,
        "periods": periods,
        "final_value": final_value,
        "total_growth": total_growth,
        "total_growth_percent": total_growth_percent,
        "formatted_final": f"${final_value:,.2f}",
        "formatted_growth": f"${total_growth:,.2f} ({total_growth_percent:.2f}%)"
    }


@tool()
def ratio(a: float, b: float) -> dict:
    """Calculate the ratio of two numbers.

    Args:
        a (float): First number
        b (float): Second number

    Returns:
        dict: Ratio a:b and simplified form
    """
    if b == 0:
        return {
            "operation": "ratio",
            "error": "Second number cannot be zero"
        }

    ratio_value = a / b

    return {
        "operation": "ratio",
        "ratio_notation": f"{a}:{b}",
        "decimal_form": ratio_value,
        "formatted": f"{ratio_value:.4f}",
        "percentage": f"{ratio_value * 100:.2f}%"
    }


@tool()
def sum_list(numbers: List[float]) -> dict:
    """Calculate the sum of a list of numbers.

    Args:
        numbers (List[float]): List of numbers to sum

    Returns:
        dict: Sum of all numbers
    """
    total = sum(numbers)

    return {
        "operation": "sum",
        "numbers": numbers,
        "count": len(numbers),
        "sum": total,
        "formatted": f"{total:,.2f}"
    }


if __name__ == "__main__":
    print("Testing Math Tool...\n")

    # Test addition
    print("1. Addition: 100 + 50")
    print(add(100, 50))

    # Test percentage change
    print("\n2. Percentage change: old=100, new=150")
    print(percentage_change(100, 150))

    # Test average
    print("\n3. Average of [10, 20, 30, 40, 50]")
    print(average([10, 20, 30, 40, 50]))

    # Test compound growth
    print("\n4. Compound growth: $1000 at 5% for 10 periods")
    print(compound_growth(1000, 5, 10))
