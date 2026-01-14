import math

class BasicMath:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def divide(a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    @staticmethod
    def factorial(n):
        return math.factorial(int(n))

    @staticmethod
    def gcd(a, b):
        return math.gcd(int(a), int(b))

    @staticmethod
    def minus(a, b):
        return a - b

    @staticmethod
    def multiply(a, b):
        return a * b

    @staticmethod
    def plus(a, b):
        return a + b

    @staticmethod
    def pow(a, b):
        return math.pow(a, b)

    @staticmethod
    def round(a):
        return round(a)

    @staticmethod
    def sqrt(a):
        return math.sqrt(a)

    @staticmethod
    def subtract(a, b):
        return a - b
