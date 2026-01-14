import math

class Quadrilateral:
    @staticmethod
    def parallelogram_area(*, base_side=None, height=None):
        if base_side is not None and height is not None:
            return base_side * height
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def rectangle_area(*, width=None, height=None):
        if width is not None and height is not None:
            return width * height
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def rectangle_diagonal(*, width=None, height=None):
        if width is not None and height is not None:
            return math.sqrt(width**2 + height**2)
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def rectangle_perimeter(*, width=None, height=None):
        if width is not None and height is not None:
            return 2 * (width + height)
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def rhombus_area(*, diagonal1=None, diagonal2=None):
        if diagonal1 is not None and diagonal2 is not None:
            return 0.5 * diagonal1 * diagonal2
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def square_area(*, side=None):
        if side is not None:
            return side**2
        raise ValueError("Insufficient parameters.")

    @staticmethod
    def trapezoid_area(*, a=None, b=None, h=None):
        if a is not None and b is not None and h is not None:
            return 0.5 * (a + b) * h
        raise ValueError("Insufficient parameters.")
