from itertools import cycle
from typing import Sequence
from numpy import ndarray
from ..utils import get_bits_required, connect
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *
from ..prebuilds.decoder import decoder


def ram(bp: Blueprint, bit_length: int, num_address: int, pos: Pos | Sequence = (0, 0, 0),
        address_divisor=1,
        pre_arr=None, pre_inputs=None, pre_outputs=None):
    pos = check_pos(pos)

    arr = pre_arr if pre_arr is not None else ndarray(
        (bit_length, num_address, 4), dtype=LogicGate)
    writers = [LogicGate(pos + (-1, 2, y), "000000", xaxis=1, zaxis=3)
               for y in range(num_address)]
    readers = [LogicGate(pos + (-1, 0, y), "000000", xaxis=1, zaxis=3)
               for y in range(num_address)]
    inputs = pre_inputs if pre_inputs is not None else [LogicGate(pos + (x, 1, -1), "FF0000", 1, xaxis=1, zaxis=3)
                                                        for x in range(bit_length)]
    outputs = pre_outputs if pre_outputs is not None else [LogicGate(pos + (x, 1, -2), "0000FF", 1, xaxis=1, zaxis=3)
                                                           for x in range(bit_length)]
    writers_binary = ndarray(
        (get_bits_required(num_address//address_divisor), 2), dtype=LogicGate)
    write_enable = LogicGate(pos + (-1, 2, -1), "FF0000", 1, xaxis=1, zaxis=3)
    readers_binary = ndarray(
        (get_bits_required(num_address//address_divisor), 2), dtype=LogicGate)
    read_enable = LogicGate(
        pos + (-1, 0, -1), "FF0000", 1, xaxis=1, zaxis=3)

    if pre_arr is None:
        for x in range(bit_length):
            for y in range(num_address):
                # if pre_arr is None:
                arr[x, y, :] = [
                    # arr.flat[y*num_address + x] = [
                    l3 := LogicGate(pos + (x, 1, y+1), "000000", xaxis=1, zaxis=-3),
                    l2 := LogicGate(pos + (x, 2, y), "FF0000", 2),
                    l1 := LogicGate(pos + (x, 3, y), "000000"),
                    l0 := LogicGate(pos + (x, 3, y), "0000FF", 2, xaxis=1, zaxis=3),
                ]
                l2.connect(l1).connect(l0).connect(l0).connect(l2)
                l0.connect(l3)
                # else:
                #     print(x, y, bit_length, num_address, arr.shape)
                #     l3, l2, l1, l0 = arr[x, y, :]
                #     # l3, l2, l1, l0 = arr.reshape(())[x, y, :]
                #     l2.connect(l1).connect(l0).connect(l2)
                #     l0.connect(l3)
    else:
        for l3, l2, l1, l0 in arr.reshape((arr.shape[0]*arr.shape[1], 4)):
            l2.connect(l1).connect(l0).connect(l2)
            l0.connect(l3)
    connect(writers, arr[:, :, 2].T)
    connect(readers, arr[:, :, 0].T)
    # connect(inputs, arr[:, :, 1])
    for i, a in zip(cycle(inputs), arr[:, :, 1].T.flat):
        connect(i, a)
    # connect(arr[:, :, 0], outputs)
    for a, o, in zip(arr[:, :, 0].T.flat, cycle(outputs)):
        connect(a, o)
    for y in range(get_bits_required(num_address//address_divisor)):
        writers_binary[y, :] = [
            LogicGate(pos + (-2, 2, y), "FF0000", 4, xaxis=1, zaxis=3),
            LogicGate(pos + (-3, 2, y), "FF0000", 1, xaxis=1, zaxis=3),
        ]
        readers_binary[y, :] = [
            LogicGate(pos + (-2, 0, y),
                      "FF0000", 4, xaxis=1, zaxis=3),
            LogicGate(pos + (-3, 0, y),
                      "FF0000", 1, xaxis=1, zaxis=3),
        ]
    decoder(bp, num_address, (0, 0, 0), writers_binary, writers,
            write_enable, address_divisor=address_divisor)
    decoder(bp, num_address, (0, 0, 0), readers_binary, readers,
            read_enable, address_divisor=address_divisor)

    if pre_arr is None:
        bp.add(arr)
    if pre_inputs is None:
        bp.add(inputs)
    if pre_outputs is None:
        bp.add(outputs)
    bp.add(writers, readers, writers_binary,
           write_enable, readers_binary, read_enable)

    return arr, inputs, outputs, writers_binary, writers, write_enable, readers_binary, readers, read_enable
