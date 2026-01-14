import math

class Circle:
    @staticmethod
    def arc_length(*, radius=None, angle=None):
        if radius is not None and angle is not None:
            return 2 * math.pi * radius * (angle / 360.0)
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def area(*, radius=None):
        if radius is not None:
            return math.pi * (radius**2)
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def perimeter(*, radius=None):
        if radius is not None:
            return 2 * math.pi * radius
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def sector_angle(*, radius=None, arc_length=None):
        if radius is not None and arc_length is not None:
            return (arc_length * 180.0) / (math.pi * radius)
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def sector_area(*, radius=None, angle=None):
        if radius is not None and angle is not None:
            return math.pi * (radius**2) * (angle / 360.0)
        raise ValueError("Insufficient parameters.")
