from typing import Sequence
from numpy import ndarray
from ..utils import get_bits_required, connect
from ..blueprint import Blueprint
from ..parts.logicgate import LogicGate
from ..parts.timer import Timer
from ..pos import *
from ..prebuilds.clock40hz import clock40hz
from ..prebuilds.decoder import decoder
from ..prebuilds.ram import ram
from ..prebuilds.register import register


def timer_ram_multiclient(bp: Blueprint, bit_length: int, num_address: int, num_clients=1, pos: Pos | Sequence = (0, 0, 0)):
    initial_part_count = len(bp.bodies[0].childs)
    pos = check_pos(pos)

    clock = clock40hz(
        bp, get_bits_required(num_address), pos + (bit_length, 0, 0))

    timers = ndarray((bit_length, 3), dtype=object)
    timer_read_write_enable = LogicGate(pos + (-1, 1, 0), "FF0000", 4)
    for x in range(bit_length):
        # timers[x] = [
        #     t0 := Timer(pos + (x % 8, 0, 2*(x//8)), "000000", ((num_address-3) // 40, (num_address-3) % 40)),
        #     l0 := LogicGate(pos + (x % 8, 1, 2*(x//8)), "000000"),
        #     l1 := LogicGate(pos + (x % 8, 1, 2*(x//8)+1), "000000", 1),
        # ]
        timers[x] = [
            t0 := Timer(pos + (x, 0, 0), "000000", ((num_address-3) // 40, (num_address-3) % 40)),
            l0 := LogicGate(pos + (x, 1, 0), "000000"),
            l1 := LogicGate(pos + (x, 1, 1), "000000", 1),
        ]
        t0.connect(l0).connect(l1).connect(t0)
    connect(timer_read_write_enable, timers[:, 1])

    for z in range(num_clients):
        cpos = pos + (0, 0, z*2)
        data = register(bp, bit_length, pos=cpos + (0, 4, 0))
        timers_readers = [LogicGate(cpos+(x, 3, 0), "000000")
                          for x in range(bit_length)]
        timers_readers_enable = LogicGate(cpos+(-1, 3, 0), "FF0000", 1)
        timers_readers_buffer = LogicGate(cpos+(-1, 5, 0), "000000")
        address = register(bp, get_bits_required(
            num_address), pos=cpos + (bit_length+1, 5, 0), OE=False)
        post_rw = register(bp, 2,
                           pos=cpos + (bit_length+1+get_bits_required(num_address)+1, 5, 0), OE=False)
        rw_inv = [
            LogicGate(
                cpos + (bit_length+1+get_bits_required(num_address)+1, 4, 0), "000000", 3),
            LogicGate(
                cpos + (bit_length+1+get_bits_required(num_address)+2, 4, 0), "000000")
        ]
        comparator = [LogicGate(cpos+(x+bit_length+1, 4, 0), "000000", 5)
                      for x in range(get_bits_required(num_address))]
        comparator_write = LogicGate(cpos+(bit_length+1, 3, 0), "000000")
        comparator_read = LogicGate(cpos+(bit_length+2, 3, 0), "000000")
        connect(post_rw[0][0, 0], rw_inv)
        connect(address[0][:, 0], comparator)
        connect(clock[:, 0], comparator)
        connect(comparator, comparator_write)
        connect(comparator, comparator_read)
        connect(rw_inv[0], comparator_write)
        connect(rw_inv[1], comparator_read)
        connect(post_rw[0][1, 0], comparator_write)
        connect(post_rw[0][1, 0], comparator_read)
        connect(comparator_write, timer_read_write_enable)
        connect(comparator_write, data[2])
        connect(data[0][:, 0], timers[:, 2])
        connect(comparator_write, post_rw[1])
        connect(comparator_read, post_rw[1])
        connect(comparator_read, timers_readers_enable)
        connect(timers_readers_enable, timers_readers_buffer)
        connect(timers_readers_buffer, data[1])
        connect(timers_readers_enable, timers_readers)
        connect(timers[:, 0], timers_readers)
        connect(timers_readers, data[0][:, 3])
        bp.add(comparator, comparator_write, comparator_read, rw_inv,
               timers_readers, timers_readers_enable, timers_readers_buffer)

    bp.add(timers, timer_read_write_enable)

    print(f"Timer ram: {bit_length*num_address} bits ({bit_length*num_address/8} bytes), "
          f"Max time delay: {num_address} ticks ({num_address/40} seconds), "
          f"Bits per part: {bit_length*num_address / (len(bp.bodies[0].childs)-initial_part_count):.2f} bits/part")
