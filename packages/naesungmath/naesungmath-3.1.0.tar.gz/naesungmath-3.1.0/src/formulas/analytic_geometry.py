import math

class AnalyticGeometry:
    @staticmethod
    def center_gravity(x1, y1, x2, y2, x3, y3):
        return ((x1 + x2 + x3) / 3.0, (y1 + y2 + y3) / 3.0)

    @staticmethod
    def eccentricity(a, b):
        if a == 0: raise ZeroDivisionError("a cannot be zero")
        return math.sqrt(1 - (b**2) / (a**2))

    @staticmethod
    def is_in_range(value, min_val, max_val):
        return min_val <= value <= max_val
