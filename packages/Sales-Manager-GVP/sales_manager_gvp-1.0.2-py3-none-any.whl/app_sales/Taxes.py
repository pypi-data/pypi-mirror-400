from .exceptions import InvalidTaxError

class taxes:
    def __init__(self, percentage):
        if not (0 <= percentage <= 1):
            raise InvalidTaxError("The tax rate must be between 0 and 1")
        self.percentage = percentage
    
    def apply_tax(self, price):
        return price * self.percentage