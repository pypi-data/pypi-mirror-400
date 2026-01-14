
import os
import sys

# keep list
keep = [
    '__init__.py',
    'basic_math.py',
    'equation.py',
    'calculus.py',
    'linear_algebra.py',
    'circle.py',
    'triangle.py',
    'quadrilateral.py',
    'polygon.py',
    'solid_3d.py',
    'analytic_geometry.py',
    'trigonometry.py',
    'arithmetic_progression.py',
    'geometric_progression.py',
    'cleanup.py' 
]

current_dir = os.path.dirname(os.path.abspath(__file__))
for file in os.listdir(current_dir):
    if file.endswith('.py') and file not in keep:
        print(f"Deleting {file}")
        os.remove(os.path.join(current_dir, file))
print("Cleanup complete.")
