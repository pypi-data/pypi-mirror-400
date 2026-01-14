from typing import Sequence
from numpy import ndarray
from ..utils import get_bits_required, connect, num_to_bit_list
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *


def clock40hz(bp: Blueprint, bit_length: int, pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)

    arr = ndarray((bit_length, 2), dtype=LogicGate)
    for x in range(bit_length):
        arr[x, :] = [
            LogicGate(pos + (x, 0, 0), "0000FF", 2 if x else 4),
            LogicGate(pos + (x, 1, 0), "000000", 0),
        ]

    connect(arr[:, 0], arr[:, 0])
    connect(arr[1:, 1], arr[1:, 0])
    connect(arr[0, 0], arr[0, 1])
    connect(arr[0, 1], arr[1:, 1])
    for x in range(1, bit_length):
        connect(arr[x, 0], arr[x+1:, 1])

    bp.add(arr)

    return arr
