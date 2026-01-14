import math

class Equation:
    @staticmethod
    def cubic_roots(a, b, c, d):
        term1 = 2 * (b**3) - (9 * a * b * c) + (27 * (a**2) * d)
        term2 = (b**2) - 3 * a * c
        discriminant_root = (term1**2 - 4 * (term2**3)) ** 0.5

        x = (0.5 * (term1 + discriminant_root)) ** (1/3)
        y = (0.5 * (term1 - discriminant_root)) ** (1/3)
        
        # Complex number handling in Python power? 
        # C# Math.Pow works for real. 
        # Python ** works for complex if needed, but original used arithmetic that implies reals usually or handled basic cases.
        # Just strictly copying the formula structure.

        return -(b / (3 * a)) - ((1 / (3 * a)) * x) - ((1 / (3 * a)) * y)

    @staticmethod
    def newton(f, count, initx=2):
        def diff(func, x, density=5):
            dx = 2 * (10 ** -density)
            dy = func(x + (10 ** -density)) - func(x - (10 ** -density))
            return dy / dx

        x_curr = initx
        for _ in range(count):
            x_curr = x_curr - f(x_curr) / diff(f, x_curr)
        return x_curr

    @staticmethod
    def quadratic_roots(a, b, c):
        discriminant = math.sqrt(b**2 - 4 * a * c)
        x1 = (-b + discriminant) / (2 * a)
        x2 = (-b - discriminant) / (2 * a)
        return (x1, x2)

    @staticmethod
    def root_and_coefficient(a, b, c, type_):
        if type_ == 1:
            return -(b / a)
        if type_ == 2:
            return (b / c)
        return None
