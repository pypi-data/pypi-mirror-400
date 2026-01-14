from typing import Sequence
from numpy import ndarray
from ..utils import get_bits_required, connect, num_to_bit_list
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *


def barrel_shifter(bp: Blueprint, bit_length: int, num_bit_shift: int, pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)
    inputs = [LogicGate(pos + (x, 0, 0), "FF0000", 1)
              for x in range(bit_length)]
    inputs_shift_binary = ndarray((num_bit_shift, 2), dtype=LogicGate)
    # always_off = LogicGate(pos + (-1, -1, 0), "000000")

    for x in range(num_bit_shift):
        inputs_shift_binary[x, :] = [
            LogicGate(pos + (x-num_bit_shift, -1, 0), "FF0000", 4),
            LogicGate(pos + (x-num_bit_shift, 0, 0), "FF0000", 1),
        ]

    arr = [
        [
            [LogicGate(pos+(x, (-y-1), 0), "000000")
             for x in range(bit_length + (2**y - 1 if y != num_bit_shift - 1 else 0))]
            for y in range(num_bit_shift)
        ],
        [
            [LogicGate(pos+((x - (2**y if y == num_bit_shift-1 else 0)), (-y-1), 1), "000000")
             for x in range(2**y, bit_length + 2**(y+1) - 1 - (2**y if y == num_bit_shift-1 else 0))]
            for y in range(num_bit_shift)
        ],
        [
            [LogicGate(pos+(x, (-y-1), 2), "000000" if y != num_bit_shift - 1 else "0000FF", 1)
             for x in range(bit_length - 1 + (2**(y+1) if y != num_bit_shift-1 else 1))]
            for y in range(num_bit_shift)
        ],
    ]

    connect(inputs, arr[0][0])
    connect(inputs, arr[1][0])
    for y in range(num_bit_shift):
        connect(arr[0][y], arr[2][y])
    for y in range(num_bit_shift-1):
        connect(arr[2][y], arr[0][y+1])
        connect(arr[1][y], arr[2][y][2**y:])
    for y in range(num_bit_shift-2):
        connect(arr[2][y], arr[1][y+1])
    connect(arr[2][-2][2**(num_bit_shift-1):], arr[1][-1])
    connect(arr[1][-1], arr[2][-1])
    for y in range(num_bit_shift):
        connect(inputs_shift_binary[y, 0], arr[0][y])
        connect(inputs_shift_binary[y, 1], arr[1][y])

    bp.add(inputs, inputs_shift_binary, arr)
    # arr = ndarray((bit_length, num_bit_shift, 3), dtype=LogicGate)
    # for x in range(num_bit_shift):
    #     inputs_shift_binary[x, :] = [
    #         LogicGate(pos + (x+bit_length+1, -1, 0), "FF0000", 4),
    #         LogicGate(pos + (x+bit_length+1, 0, 0), "FF0000", 1),
    #     ]
    # for x in range(bit_length):
    #     for y in range(num_bit_shift):
    #         arr[x, y, :] = [
    #             LogicGate(pos + (x, -y-1, 0), "000000"),
    #             LogicGate(pos + (x, -y-1, 1), "000000"),
    #             LogicGate(pos + (x, -y-1, 2), "000000"
    #                       if y + 1 < num_bit_shift else "0000FF", 1),
    #         ]
    # always_off.connect(always_off)

    # connect(inputs, arr[:, 0, 0])
    # connect(inputs, arr[1:, 0, 1])
    # connect(arr[:, :, 0], arr[:, :, 2])
    # connect(arr[:, :, 1], arr[:, :, 2])
    # connect(arr[:, :, 2], arr[:, 1:, 0])
    # for y in range(num_bit_shift):
    #     if y + 1 < num_bit_shift:
    #         connect(arr[:, y, 2], arr[2**(y+1):, y+1, 1])
    #     connect(always_off, arr[:2**y, y, 1])
    #     connect(inputs_shift_binary[y, 0], arr[:, y, 0])
    #     connect(inputs_shift_binary[y, 1], arr[:, y, 1])

    # bp.add(inputs, inputs_shift_binary, arr, always_off)

    # return inputs, inputs_shift_binary, arr, always_off
