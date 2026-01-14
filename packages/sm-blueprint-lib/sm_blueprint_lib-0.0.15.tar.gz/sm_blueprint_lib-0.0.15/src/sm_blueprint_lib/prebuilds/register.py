from typing import Sequence
from numpy import ndarray
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *
from ..prebuilds.counter import counter, counter_decrement


def register(bp: Blueprint,
             bit_length: int,
             OE=True,
             pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)
    write = LogicGate(pos + (-1, 2 if OE else 1, 0), "FF0000", 1)
    if OE:
        output_enable = LogicGate(pos + (-1, 0, 0), "FF0000", 1)
        arr = ndarray((bit_length, 4), LogicGate)
        for x in range(bit_length):
            arr[x] = [
                l0 := LogicGate(pos + (x, 0, 0), "000000"),
                l1 := LogicGate(pos + (x, 1, 0), "0000FF", 2),
                l2 := LogicGate(pos + (x, 2, 0), "000000"),
                l3 := LogicGate(pos + (x, 3, 0), "FF0000", 2),
            ]
            l3.connect(l2).connect(l1).connect(l1).connect(l3)
            l1.connect(l0)
            write.connect(l2)
            output_enable.connect(l0)
        bp.add(output_enable)
    else:
        arr = ndarray((bit_length, 3), LogicGate)
        for x in range(bit_length):
            arr[x] = [
                l0 := LogicGate(pos + (x, 0, 0), "0000FF", 2),
                l1 := LogicGate(pos + (x, 1, 0), "000000"),
                l2 := LogicGate(pos + (x, 2, 0), "FF0000", 2),
            ]
            l2.connect(l1).connect(l0).connect(l0).connect(l2)
            write.connect(l1)
    bp.add(arr, write)
    if OE:
        return arr, write, output_enable
    else:
        return arr, write


def counter_register(bp: Blueprint,
                     bit_length: int,
                     OE=True,
                     with_increment=True,
                     with_decrement=True,
                     pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)
    r = register(bp, bit_length, OE, pos)

    if with_decrement:
        cdec = counter_decrement(bp,
                                 bit_length=bit_length,
                                 pos=pos+(0, OE, 1),
                                 precreated_swxors=r[0][:, int(OE)])
    if with_increment:
        cinc = counter(bp,
                       bit_length=bit_length,
                       pos=pos+(0, OE, 1+with_decrement),
                       precreated_swxors=r[0][:, int(OE)])
    if with_increment and with_decrement:
        return r, cinc[0][:, 1], cinc[1], cdec[0][:, 1], cdec[1]
    elif with_increment:
        return r, cinc[0][:, 1], cinc[1]
    else:
        return r, cdec[0][:, 1], cdec[1]
