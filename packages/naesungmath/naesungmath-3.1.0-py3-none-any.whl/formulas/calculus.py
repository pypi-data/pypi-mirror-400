import math
from .basic_math import BasicMath

class Calculus:
    @staticmethod
    def diff(f, x, h=1e-5):
        return (f(x + h) - f(x)) / h

    @staticmethod
    def infinite_series(type_, x=0):
        if type_ == 4: return 1.0 / (1.0 - x)
        if type_ == 1: return 2.0
        if type_ == 2: return 2.0 / 3.0
        if type_ == 3: return math.exp(x)
        return 0

    @staticmethod
    def integral(f, start, end, density=100):
        step = (end - start) / density
        area = 0
        for i in range(int(density)):
            x = start + i * step
            area += f(x) * step
        return area

    @staticmethod
    def maclaurin(f, x, n):
        return Calculus.taylor(f, x, 0, n)

    @staticmethod
    def sigma(start, end, func):
        sum_val = 0
        for i in range(start, end + 1):
            sum_val += func(i)
        return sum_val

    @staticmethod
    def sigma_cubed(n):
        return (n * (n + 1) / 2) ** 2

    @staticmethod
    def sigma_squared(n):
        return n * (n + 1) * (2 * n + 1) / 6.0

    @staticmethod
    def taylor(f, x, a, n):
        sum_val = 0
        for i in range(n):
            sum_val += (Calculus._diff_n(f, a, i) / BasicMath.factorial(i)) * ((x - a) ** i)
        return sum_val

    @staticmethod
    def _diff_n(f, x, n):
        if n == 0: return f(x)
        if n == 1: return Calculus.diff(f, x)
        h = 1e-4
        return (Calculus._diff_n(f, x + h, n - 1) - Calculus._diff_n(f, x - h, n - 1)) / (2 * h)
