"""Basic example demonstrating prsdm mathematical operations."""

from prsdm.operations import add, divide, multiply, subtract


def main():
    """Example usage of prsdm mathematical operations."""
    # Addition
    result = add(5, 3)
    print(f"5 + 3 = {result}")

    # Subtraction
    result = subtract(10, 4)
    print(f"10 - 4 = {result}")

    # Multiplication
    result = multiply(7, 2)
    print(f"7 * 2 = {result}")

    # Division
    result = divide(15, 3)
    print(f"15 / 3 = {result}")

    # More complex example
    a, b = 20, 4
    sum_result = add(a, b)
    product_result = multiply(a, b)
    print(f"\nFor a={a} and b={b}:")
    print(f"Sum: {sum_result}, Product: {product_result}")


if __name__ == "__main__":
    main()
