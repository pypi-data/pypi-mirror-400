from typing import Sequence
from numpy import ndarray
from ..utils import get_bits_required, connect, num_to_bit_list
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..pos import *


def decoder(bp: Blueprint, num_address: int, pos: Pos | Sequence = (0, 0, 0),
            precreated_inputs_binary=None, precreated_outputs=None, precreated_output_enable=None,
            address_divisor=1, with_enable=True):
    pos = check_pos(pos)

    if precreated_inputs_binary is not None:
        inputs_binary = precreated_inputs_binary
    else:
        inputs_binary = ndarray(
            (get_bits_required(num_address), 2), dtype=LogicGate)
    if precreated_outputs is not None:
        outputs = precreated_outputs
    else:
        outputs = [LogicGate(pos + (x+1, 0, 0), "0000FF")
                   for x in range(num_address)]
    if with_enable:
        if precreated_output_enable is not None:
            output_enable = precreated_output_enable
        else:
            output_enable = LogicGate(pos + (0, 0, 0), "FF0000", 1)

    if precreated_inputs_binary is None:
        for b in range(get_bits_required(num_address)):
            inputs_binary[b, :] = [
                LogicGate(pos + (b+1, 1, 0), "FF0000", 4),
                LogicGate(pos + (b+1, 2, 0), "FF0000", 1),
            ]

    for x in range(num_address):
        bit_mask = num_to_bit_list(
            x//address_divisor, get_bits_required(num_address//address_divisor))
        connect(inputs_binary[~bit_mask, 0], outputs[x])
        connect(inputs_binary[bit_mask, 1], outputs[x])
    if with_enable:
        connect(output_enable, outputs)

    if precreated_inputs_binary is None:
        bp.add(inputs_binary)
    if precreated_outputs is None:
        bp.add(outputs)
    if with_enable:
        if precreated_output_enable is None:
            bp.add(output_enable)

    if with_enable:
        return inputs_binary, outputs, output_enable
    else:
        return inputs_binary, outputs
