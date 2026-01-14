from .constants import ROTATION
from .pos import Pos
from .bases.parts.basepart import BasePart


def rotate(gates: list, center: Pos):
    """Rotates a list of gate

    Args:
        gates (list): list of gates to rotate.
        center (Pos): Center point to rotate gates.

    """
    for gate in gates:
        temp = gate.pos
        # todo everything :)
    pass
