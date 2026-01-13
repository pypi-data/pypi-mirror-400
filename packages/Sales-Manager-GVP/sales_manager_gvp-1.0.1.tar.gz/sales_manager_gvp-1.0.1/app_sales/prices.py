class prices:
    @staticmethod
    def calculate_final_price(price_base, tax, discount):
        return price_base + tax - discount