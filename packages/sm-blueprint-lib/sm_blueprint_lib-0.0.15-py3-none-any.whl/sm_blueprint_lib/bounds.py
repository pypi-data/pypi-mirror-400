from dataclasses import dataclass


@dataclass
class Bounds:
    """Class that represents the bounds of a boundable block (x, y, z)
    """
    x: int
    y: int
    z: int
