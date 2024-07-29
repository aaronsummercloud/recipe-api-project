from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):

    def test_add_numbers(self):
        result = calc.add(5, 6)

        self.assertEqual(result, 11)

    def test_subtract_numbers(self):
        result = calc.subtract(5, 6)

        self.assertEqual(result, -1)

    def test_multiply_numbers(self):
        result = calc.multiply(1, 2)

        self.assertEqual(result, 2)