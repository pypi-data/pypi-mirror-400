from typing import Sequence
from numpy import ndarray
from ..utils import connect
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *


def comparator(bp: Blueprint,
               bit_length: int,
               pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)
    inputs = ndarray((bit_length, 4), dtype=LogicGate)
    ands_2 = ndarray((bit_length, 2), dtype=LogicGate)
    nors_3 = ndarray(bit_length, dtype=LogicGate)
    ands_4 = ndarray(2 * (bit_length - 1) + 1, dtype=LogicGate)
    ors_5 = ndarray(2, dtype=LogicGate)
    inputs[:, 0] = [
        LogicGate(pos+(x, -1, 0), "FF0000", 4)
        for x in range(bit_length)
    ]
    inputs[:, 1] = [
        LogicGate(pos+(x, 0, 0), "FF0000", 1)
        for x in range(bit_length)
    ]
    inputs[:, 2] = [
        LogicGate(pos+(x, -1, 2), "FF0000", 4)
        for x in range(bit_length)
    ]
    inputs[:, 3] = [
        LogicGate(pos+(x, 0, 2), "FF0000", 1)
        for x in range(bit_length)
    ]
    for x in range(bit_length):
        ands_2[x, :] = [
            LogicGate(pos+(x, -2, 0), "000000"),
            LogicGate(pos+(x, -2, 1), "000000"),
        ]
        nors_3[x] = LogicGate(pos+(x, -2, 2), "000000", 4)

    for n in range(2 * (bit_length - 1) + 1):
        if n == 0:
            ands_4[n] = LogicGate(pos+(1, -4, 0), "0000FF")
        else:
            ands_4[n] = LogicGate(pos+((n-1)//2, -3, (n-1) % 2), "000000")

    ors_5[:] = [
        LogicGate(pos+(0, -4, 0), "0000FF", 1),
        LogicGate(pos+(2, -4, 0), "0000FF", 1),
    ]

    connect(inputs[:, 0], ands_2[:, 1])
    connect(inputs[:, 1], ands_2[:, 0])
    connect(inputs[:, 2], ands_2[:, 0])
    connect(inputs[:, 3], ands_2[:, 1])

    connect(ands_2, nors_3)

    connect(ands_2.flat, ands_4[1:])
    for x in range(bit_length):
        connect(nors_3[x], ands_4[:2*x+1])

    connect(ands_4[1::2], ors_5[0])
    connect(ands_4[2::2], ors_5[1])
    connect(ands_2[-1, 0], ors_5[0])
    connect(ands_2[-1, 1], ors_5[1])

    bp.add(inputs, ands_2, nors_3, ands_4, ors_5)

    return inputs, ands_2, nors_3, ands_4, ors_5
