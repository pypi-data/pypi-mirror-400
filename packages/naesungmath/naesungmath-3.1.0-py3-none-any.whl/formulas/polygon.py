import math

class Polygon:
    @staticmethod
    def area(n, side_length):
        return (n * (side_length**2)) / (4 * math.tan(math.pi / n))

    @staticmethod
    def diagonal_count(n):
        return n * (n - 3) / 2

    @staticmethod
    def euler_theorem(v, e, f):
        return (v - e + f) == 2

    @staticmethod
    def hexagon_area(side):
        return (3 * math.sqrt(3) * (side**2)) / 2

    @staticmethod
    def interior_angle_deg(n):
        return 180 * (n - 2) / n

    @staticmethod
    def interior_angle_rad(n):
        return math.pi * (n - 2) / n

    @staticmethod
    def interior_angle_sum_deg(n):
        return 180 * (n - 2)

    @staticmethod
    def interior_angle_sum_rad(n):
        return math.pi * (n - 2)

    @staticmethod
    def pentagon_area(side):
        return (math.sqrt(5 * (5 + 2 * math.sqrt(5))) * (side**2)) / 4

    @staticmethod
    def pentagon_diagonal(side):
        return (1 + math.sqrt(5)) / 2 * side

    @staticmethod
    def pentagon_height(side):
        return (math.sqrt(5 + 2 * math.sqrt(5)) * side) / 2
