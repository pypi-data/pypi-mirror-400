import math

class Solid3D:
    # --- Cone ---

    @staticmethod
    def cone_area(*, radius=None, height=None):
        if radius is not None and height is not None:
             # pi * r * (r + sqrt(h^2 + r^2))
            return math.pi * radius * (radius + math.sqrt(height**2 + radius**2))
        raise ValueError("Insufficient parameters for cone_area(radius, height).")

    @staticmethod
    def cone_volume(*, radius=None, height=None):
        if radius is not None and height is not None:
            # (1/3) * pi * r^2 * h
            return (1/3) * math.pi * (radius**2) * height
        raise ValueError("Insufficient parameters for cone_volume(radius, height).")

    # --- Cube ---

    @staticmethod
    def cube_area(side):
        return 6 * (side**2)

    @staticmethod
    def cube_volume(side):
        return side**3

    # --- Cuboid ---

    @staticmethod
    def cuboid_area(length, width, height):
        return 2 * ((length * width) + (width * height) + (height * length))

    @staticmethod
    def cuboid_diagonal(length, width, height):
        return math.sqrt(length**2 + width**2 + height**2)

    @staticmethod
    def cuboid_volume(length, width, height):
        return length * width * height

    # --- Cylinder ---

    @staticmethod
    def cylinder_area(*, radius=None, height=None):
        if radius is not None and height is not None:
            # 2*pi*r*h + 2*pi*r^2
            return (2 * math.pi * radius * height) + (2 * math.pi * (radius**2))
        raise ValueError("Insufficient parameters for cylinder_area(radius, height).")

    @staticmethod
    def cylinder_volume(*, radius=None, height=None):
        if radius is not None and height is not None:
            return math.pi * (radius**2) * height
        raise ValueError("Insufficient parameters for cylinder_volume(radius, height).")

    # --- Sphere ---

    @staticmethod
    def sphere_area(radius):
        return 4 * math.pi * (radius**2)

    @staticmethod
    def sphere_volume(radius):
        return (4/3) * math.pi * (radius**3)

    # --- SquarePyramid ---

    @staticmethod
    def square_pyramid_area(*, base_side=None, height=None, slant_edge=None):
        # Case 1: base_side (a) and slant_edge (b) known (Original 'ab')
        # Matches C# logic
        if base_side is not None and slant_edge is not None:
            a = base_side
            b = slant_edge
            return (a * math.sqrt(4 * (b**2) - (a**2))) + (a**2)

        # Case 2: base_side (a) and height (h) known
        if base_side is not None and height is not None:
            a = base_side
            h = height
            return (a * math.sqrt(4 * (h**2) - (a**2))) + (a**2)

        raise ValueError("Insufficient parameters for square_pyramid_area. Required: {base_side, slant_edge} or {base_side, height}")

    @staticmethod
    def square_pyramid_height(*, base_side=None, slant_edge=None):
        if base_side is not None and slant_edge is not None:
            a = base_side
            b = slant_edge
            return math.sqrt((b**2) - ((a**2) / 2))
        raise ValueError("Insufficient parameters for square_pyramid_height(base_side, slant_edge).")

    @staticmethod
    def square_pyramid_volume(*, base_side=None, height=None, slant_edge=None):
        # Case 1: base_side (a) and height (h) known
        if base_side is not None and height is not None:
            a = base_side
            h = height
            return (1/3) * (a**2) * h

        # Case 2: base_side (a) and slant_edge (b) known
        if base_side is not None and slant_edge is not None:
            a = base_side
            b = slant_edge
            return (1/3) * (a**2) * math.sqrt((b**2) - ((a**2) / 2))

        raise ValueError("Insufficient parameters for square_pyramid_volume. Required: {base_side, height} or {base_side, slant_edge}")

    # --- Tetrahedron ---

    @staticmethod
    def tetrahedron_area(side):
        return math.sqrt(3) * (side**2)

    @staticmethod
    def tetrahedron_height(side):
        return math.sqrt(2/3) * side

    @staticmethod
    def tetrahedron_volume(side):
        return (math.sqrt(2) / 12) * (side**3)

    # --- Triangular Pyramid ---

    @staticmethod
    def triangular_pyramid_volume(*, base_area=None, height=None):
        if base_area is not None and height is not None:
            return (1/3) * base_area * height
        raise ValueError("Insufficient parameters for triangular_pyramid_volume(base_area, height).")
