from typing import Sequence
from numpy import array, ndarray
from ..utils import get_bits_required, connect, num_to_bit_list
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..parts.sensor import Sensor5
from ..parts.timer import Timer
from ..pos import *


def distance_sensor(bp: Blueprint,
                    sensor_range: range,
                    pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)
    bit_length = get_bits_required(len(sensor_range))
    out = [LogicGate(pos + (x, 0, 0), "0000FF", 2) for x in range(bit_length)]
    out = array(out, dtype=LogicGate)
    sensors = [Sensor5(pos + (bit_length, -1, 1), "000000",
                       (False, True, "FFFFFF", False, x), xaxis=-3, zaxis=1) for x in sensor_range]

    current_output_state = 0
    for target in reversed(range(len(sensor_range))):
        difference = current_output_state ^ (target+1)
        if difference:
            bit_mask = num_to_bit_list(difference, bit_length)
            connect(sensors[target], out[bit_mask])
            current_output_state ^= difference

    bp.add(out, sensors)
    return out, sensors


def distance_sensor_raycast(bp: Blueprint,
                            sensor_range: range,
                            pos: Pos | Sequence = (0, 0, 0)):
    pos = check_pos(pos)
    bit_length = len(sensor_range)
    out = [LogicGate(pos + (x, 0, 0), "0000FF", 2) for x in range(bit_length)]
    sensors = [Sensor5(pos + (bit_length, -1, 0), "000000",
                       (False, True, "FFFFFF", False, x), xaxis=1, zaxis=3) for x in sensor_range]

    connect(sensors, out)

    bp.add(out, sensors)
    return out, sensors
