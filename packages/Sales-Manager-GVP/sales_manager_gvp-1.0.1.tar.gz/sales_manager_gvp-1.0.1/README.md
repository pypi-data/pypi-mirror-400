# Sales Manager

This package provides functionalities for managing sales, including price calculations, taxes, and discounts.

## Installation

You can install the package using:

```bash
pip install sales-manager

```

## Example of use

```python
from app_sales.sales_manager import SalesManager

def main():
    # Base price of the product
    base_price = 100.0

    # Tax and discount must be values between 0 and 1
    tax_percentage = 0.05      # 5% tax
    discount_percentage = 0.10 # 10% discount

    # Create a SalesManager instance
    manager = SalesManager(base_price, tax_percentage, discount_percentage)

    # Calculate the final price after tax and discount
    final_price = manager.calculate_final_price()

    # Display results
    print(f"Base price: ${base_price}")
    print(f"Tax: {tax_percentage * 100}%")
    print(f"Discount: {discount_percentage * 100}%")
    print(f"Final price: ${final_price}")

if __name__ == "__main__":
    main()

```
