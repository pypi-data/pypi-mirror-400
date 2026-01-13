from .exceptions import DiscountInvalidError

class discounts:
    def __init__(self, percentage):
        if not (0 <= percentage <= 1):
            raise DiscountInvalidError("The discount percentage must be between 0 and 1")
        self.percentage = percentage
    
    def apply_discount(self, price):
        return price * self.percentage