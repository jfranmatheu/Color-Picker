from mathutils import Vector

LEFT = 0
RIGHT = 1
TOP = 2
BOTTOM = 3

OUTER = 0
INNER = 1


class Anchor:
    def __init__(self, fxi: float, fxf: float, fyi: float, fyf: float) -> object:
        self.min = Vector((fxi, fyi))
        self.max = Vector((fxf, fyf))
