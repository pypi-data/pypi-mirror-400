import unittest
from app_sales.sales_manager import SalesManager
from app_sales.exceptions import InvalidTaxError, DiscountInvalidError

class TestSalesManager(unittest.TestCase):
    
    def test_final_price_calculation(self):
        manager = SalesManager(100.0, 0.05, 0.10)
        self.assertEqual(manager.calculate_final_price(), 95.0)
    
    def test_invalid_tax(self):
        with self.assertRaises(InvalidTaxError):
            SalesManager(100.0, 1.5, 0.10)
    
    def test_invalid_discount(self):
        with self.assertRaises(DiscountInvalidError):
            SalesManager(100.0, 0.05, 1.5)

if __name__ == "__main__":
    unittest.main()