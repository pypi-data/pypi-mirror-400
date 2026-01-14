from typing import Sequence
from numpy import ndarray
from ..utils import get_bits_required, connect, num_to_bit_list
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *


def counter(bp: Blueprint,
            bit_length: int,
            pos: Pos | Sequence = (0, 0, 0),
            precreated_swxors=None, precreated_ands=None, precreated_count=None):
    pos = check_pos(pos)
    arr = ndarray((bit_length, 2), dtype=LogicGate)
    count = precreated_count if precreated_count is not None else LogicGate(
        pos + (-1, 1, 0), "FF0000", 1)
    for x in range(bit_length):
        arr[x, :] = [
            precreated_swxors[x] if precreated_swxors is not None else LogicGate(
                pos + (x, 0, 0), "0000FF", 2),
            precreated_ands[x] if precreated_ands is not None else LogicGate(
                pos + (x, 1, 0), "000000"),
        ]
    if precreated_swxors is None:
        connect(arr[:, 0], arr[:, 0])
    connect(arr[:, 1], arr[:, 0])
    for x in range(bit_length):
        connect(arr[x, 0], arr[x+1:, 1])
    connect(count, arr[:, 1])

    if precreated_swxors is None:
        bp.add(arr[:, 0])
    if precreated_ands is None:
        bp.add(arr[:, 1])
    if precreated_count is None:
        bp.add(count)
    return arr, count


def counter_decrement(bp: Blueprint,
                      bit_length: int,
                      pos: Pos | Sequence = (0, 0, 0),
                      precreated_swxors=None, precreated_nors=None, precreated_count_nor=None):
    pos = check_pos(pos)
    arr = ndarray((bit_length, 2), dtype=LogicGate)
    count = precreated_count_nor if precreated_count_nor is not None else LogicGate(
        pos + (-1, 1, 0), "FF0000", 4)
    for x in range(bit_length):
        arr[x, :] = [
            precreated_swxors[x] if precreated_swxors is not None else LogicGate(
                pos + (x, 0, 0), "0000FF", 2),
            precreated_nors[x] if precreated_nors is not None else LogicGate(
                pos + (x, 1, 0), "000000", 4),
        ]
    if precreated_swxors is None:
        connect(arr[:, 0], arr[:, 0])
    connect(arr[:, 1], arr[:, 0])
    for x in range(bit_length):
        connect(arr[x, 0], arr[x+1:, 1])
    connect(count, arr[:, 1])

    if precreated_swxors is None:
        bp.add(arr[:, 0])
    if precreated_nors is None:
        bp.add(arr[:, 1])
    if precreated_count_nor is None:
        bp.add(count)
    return arr, count
