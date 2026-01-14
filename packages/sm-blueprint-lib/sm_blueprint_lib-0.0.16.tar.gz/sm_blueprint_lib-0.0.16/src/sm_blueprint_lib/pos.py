from dataclasses import dataclass
from typing import Sequence


@dataclass
class Pos:
    """Class that represents the position of a block (x, y, z)
    """
    x: int
    y: int
    z: int

    def __add__(self, o: "Pos" | Sequence):
        if isinstance(o, Pos):
            return Pos(self.x + o.x, self.y + o.y, self.z + o.z)
        return Pos(self.x + o[0], self.y + o[1], self.z + o[2])


def check_pos(pos: Sequence | dict) -> Pos:
    """Converts a Sequence or dict into a Pos class if it wasn't already.

    Args:
        pos (Sequence | dict): The Sequence or dict to be converted.

    Returns:
        Pos: The converted Pos.
    """
    if not isinstance(pos, Pos):
        if isinstance(pos, Sequence):
            pos = Pos(*list(pos))
        else:
            pos = Pos(**pos)
    return pos
