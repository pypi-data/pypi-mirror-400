from typing import Sequence
from numpy import ndarray
from ..utils import get_bits_required, connect, num_to_bit_list
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *


def simple_adder_subtractor(bp: Blueprint,
                            bit_length: int,
                            pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)
    input_a = [LogicGate(pos+(x, 0, 2), "FF0000", 1)
               for x in range(bit_length)]
    input_b = [LogicGate(pos+(x, 0, 0), "FF0000", 2)
               for x in range(bit_length)]
    and_0 = [LogicGate(pos+(x, -1, 2), "000000", 0)
             for x in range(bit_length)]
    xor_0 = [LogicGate(pos+(x, -1, 0), "000000", 2)
             for x in range(bit_length)]
    or_0 = [LogicGate(pos+((x, -2, 0) if x + 1 != bit_length else (x+1, -2, 2)), "000000" if x + 1 != bit_length else "0000FF", 1)
            for x in range(bit_length)]
    and_1 = [LogicGate(pos+(x, -2, 1), "000000", 0)
             for x in range(bit_length)]
    xor_1 = [LogicGate(pos+(x, -2, 2), "0000FF", 2)
             for x in range(bit_length)]
    carry_in = LogicGate(pos+(-1, -2, 0), "FF0000", 1)

    connect(input_a, and_0)
    connect(input_a, xor_0)
    connect(input_b, and_0)
    connect(input_b, xor_0)
    connect(and_0, or_0)
    connect(xor_0, and_1)
    connect(xor_0, xor_1)
    connect(and_1, or_0)
    connect(or_0, and_1[1:])
    connect(or_0, xor_1[1:])
    connect(carry_in, and_1[0])
    connect(carry_in, xor_1[0])
    connect(carry_in, input_b)

    bp.add(input_a, input_b, and_0, xor_0, or_0, and_1, xor_1, carry_in)
    return input_a, input_b, and_0, xor_0, or_0, and_1, xor_1, carry_in
