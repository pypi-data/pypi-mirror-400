import math

class Triangle:
    @staticmethod
    def area(*, base_side=None, height=None, side_a=None, side_b=None, side_c=None, angle=None,
             equilateral_side=None, circum_radius=None, in_radius=None):
        
        # 1. Base and Height
        if base_side is not None and height is not None:
            return 0.5 * base_side * height

        # 2. SAS
        if side_a is not None and side_b is not None and angle is not None:
            return 0.5 * side_a * side_b * math.sin(angle)

        # 3. Equilateral
        if equilateral_side is not None:
            return (math.sqrt(3) / 4) * (equilateral_side**2)

        # 4. Heron
        if side_a is not None and side_b is not None and side_c is not None and circum_radius is None and in_radius is None:
            a, b, c = side_a, side_b, side_c
            cos_theta = (a**2 + b**2 - c**2) / (2 * a * b)
            sin_theta = math.sqrt(1 - cos_theta**2)
            return (a * b * sin_theta) / 2

        # 5. Circumscribed
        if circum_radius is not None:
            if side_a is not None and side_b is not None and side_c is not None:
                return (side_a * side_b * side_c) / (4 * circum_radius)

        # 6. Inscribed
        if in_radius is not None and side_a is not None and side_b is not None and side_c is not None:
            return (side_a + side_b + side_c) / 2 * in_radius

        raise ValueError("Insufficient or ambiguous parameters for Triangle area.")

    @staticmethod
    def area_from_angles(angle_a, angle_b, angle_c, circum_radius):
         # This is a specific formula name, but let's encourage kwarg usage anyway if it had optional params.
         # For fixed params, positional is fine, but prompt says "Smart Solver" logic.
         return 2 * (circum_radius**2) * math.sin(angle_a) * math.sin(angle_b) * math.sin(angle_c)

    @staticmethod
    def equilateral_height(side):
        return (math.sqrt(3) / 2) * side

    @staticmethod
    def pythagoras(a, b):
        return math.sqrt(a**2 + b**2)
