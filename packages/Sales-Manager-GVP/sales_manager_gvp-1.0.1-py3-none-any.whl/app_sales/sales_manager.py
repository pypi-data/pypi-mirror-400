from .discounts import discounts
from .Taxes import taxes
from .prices import prices

class SalesManager:
    def __init__(self, price_base, tax_percentage, discount_percentage):
        self.price_base = price_base
        self.tax = taxes(tax_percentage)
        self.discounts = discounts(discount_percentage)
    
    def calculate_final_price(self):
        tax_applied = self.tax.apply_tax(self.price_base)
        discount_applied = self.discounts.apply_discount(self.price_base)
        price_final = prices.calculate_final_price(self.price_base, tax_applied, discount_applied)
        return round(price_final, 2)
