import math

class Trigonometry:
    @staticmethod
    def degree_to_rad(degrees):
        return degrees * (math.pi / 180.0)

    @staticmethod
    def radian(a):
        return Trigonometry.degree_to_rad(a)

    @staticmethod
    def rad_to_degree(radians):
        return radians * (180.0 / math.pi)
