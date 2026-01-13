import sys

sys.path.insert(0, "/home/nicolas/Documents/projet/JLC2KiCad_lib")

from JLC2KiCadLib.footprint.footprint_handlers import svg_arc_to_points

# Test 1: Simple arc
print("=== Test 1: svg_arc_to_points ===")
# Quarter circle arc from (0, 100) to (100, 0) with radius 100
points = svg_arc_to_points(
    x1=0,
    y1=100,
    rx=100,
    ry=100,
    rotation=0,
    large_arc_flag=0,
    sweep_flag=1,
    x2=100,
    y2=0,
)
print(f"Arc points count: {len(points)}")
print(f"Start should be near (0, 100), first point: {points[0] if points else 'None'}")
print(f"End should be (100, 0), last point: {points[-1] if points else 'None'}")

# Test 2: Full path with arc
print("\n=== Test 2: Full SOLIDREGION path parsing ===")
import re

path = "M 100 100 L 200 100 A 50 50 0 0 1 200 200 L 100 200 Z"

command_pattern = re.compile(
    r"([MLAZ])\s*"
    r"((?:[-+]?\d*\.?\d+[\s,]*)*)",
    re.IGNORECASE,
)
number_pattern = re.compile(r"[-+]?\d*\.?\d+")

points = []
current_pos = (0.0, 0.0)

for match in command_pattern.finditer(path):
    cmd = match.group(1).upper()
    params_str = match.group(2)
    params = [float(n) for n in number_pattern.findall(params_str)]
    print(f"Command: {cmd}, Params: {params}")

    if cmd == "M" or cmd == "L":
        if len(params) >= 2:
            current_pos = (params[0], params[1])
            points.append(current_pos)
    elif cmd == "A":
        if len(params) >= 7:
            arc_points = svg_arc_to_points(
                current_pos[0],
                current_pos[1],
                params[0],
                params[1],
                params[2],
                int(params[3]),
                int(params[4]),
                params[5],
                params[6],
            )
            points.extend(arc_points)
            current_pos = (params[5], params[6])

print(f"\nTotal points: {len(points)}")
for i, p in enumerate(points):
    print(f"  {i}: ({p[0]:.2f}, {p[1]:.2f})")
