from itertools import cycle
from typing import Sequence
from numpy import array, clip, ndarray
from ..utils import get_bits_required, connect, num_to_bit_list
from ..bases.parts.baseinteractablepart import BaseInteractablePart
from ..bases.parts.baselogicpart import BaseLogicPart
from ..blueprint import Blueprint
from ..constants import TICKS_PER_SECOND
from ..parts.logicgate import LogicGate
from ..parts.timer import Timer
from ..pos import *
from ..prebuilds.clock40hz import clock40hz
from ..prebuilds.counter import counter
from ..prebuilds.decoder import decoder
from ..prebuilds.ram import ram
from ..prebuilds.register import register


def timer_ram_cached(
        bp: Blueprint,
        bit_length: int,
        num_address_per_cache: int,
        num_caches: int,
        num_timer_banks: int,
        num_caches_per_bank: int,
        pos: Pos | Sequence = (0, 0, 0)):
    initial_part_count = len(bp.bodies[0].childs)
    total_bits = bit_length*num_address_per_cache*num_timer_banks*num_caches_per_bank
    cached_bits = bit_length*num_address_per_cache*num_caches
    cached_addresses = num_address_per_cache*num_caches
    banked_addresses = num_address_per_cache*num_timer_banks
    total_pages = num_timer_banks*num_caches_per_bank

    pos = check_pos(pos)

    clock = clock40hz(
        bp, get_bits_required(num_caches_per_bank), pos + (-get_bits_required(total_pages) - 5, 7, num_caches))

    cache = ram(bp,
                bit_length,
                cached_addresses,
                pos + (0, 5, 0))
    cache_arr = ndarray((bit_length, cached_addresses, 4), dtype=LogicGate)
    cache_full_page_in = ndarray(
        (bit_length, num_address_per_cache), dtype=LogicGate)
    cache_full_page_out = ndarray(
        (bit_length, num_address_per_cache), dtype=LogicGate)

    timer_bank = ndarray(
        (bit_length, banked_addresses, 5), dtype=BaseLogicPart)

    timer_bank_decoder_read = [LogicGate(
        pos + (bit_length*3, 8, z), "000000", xaxis=1, zaxis=3) for z in range(banked_addresses)]
    timer_bank_decoder_read_in = ndarray(
        (get_bits_required(num_timer_banks), 2), dtype=LogicGate)
    timer_bank_decoder_read_enable = LogicGate(
        pos + (bit_length*3, 8, -1), "FF0000", 1, xaxis=1, zaxis=3)

    timer_bank_decoder_write_keep = ndarray(
        (banked_addresses, 2), dtype=LogicGate)
    timer_bank_decoder_write_keep_in = ndarray(
        (get_bits_required(num_timer_banks), 4), dtype=LogicGate)
    timer_bank_decoder_write_keep_enable = (LogicGate(pos + (bit_length*3, 6, -1), "FF0000", 1, xaxis=1, zaxis=3),
                                            LogicGate(pos + (bit_length*3, 6, -2), "FF0000", 1, xaxis=1, zaxis=3))

    cache_pointer = counter(bp, get_bits_required(num_caches),
                            pos + (-get_bits_required(total_pages) - 5, 5, num_caches))

    # cache_table_offset_x = int(
    #     clip(get_bits_required(total_pages) - bit_length + 2, 0, None))
    cache_table = ram(bp,
                      bit_length=get_bits_required(total_pages) + 2,
                      num_address=num_caches,
                      #   pos=pos + (-cache_table_offset_x, 5, cached_addresses+2))
                      pos=pos + (-get_bits_required(total_pages) - 5, 5, 0))

    cache_table_lookup = ndarray(
        (get_bits_required(total_pages), num_caches), dtype=LogicGate)
    cache_table_lookup_in = [LogicGate(pos + (x-get_bits_required(total_pages) - 5, 4, -1),
                                       "ff0000", 1, xaxis=1, zaxis=3) for x in range(get_bits_required(total_pages))]
    cache_table_lookup_out = array([LogicGate(pos + (x-get_bits_required(total_pages) - 5, 4, -2),
                                   "0000ff", 1, xaxis=1, zaxis=3) for x in range(get_bits_required(num_caches)+1)], dtype=LogicGate)
    cache_table_lookup_dec = [LogicGate(pos + (-get_bits_required(
        total_pages) - 6, 4, z), "000000", xaxis=1, zaxis=3) for z in range(num_caches)]

    for x in range(bit_length):
        for y in range(cached_addresses):
            cache_arr[x, y, :] = [
                LogicGate(pos + (x, 3, y), "000000"),
                LogicGate(pos + (x, 4, y), "FF0000", 2),
                LogicGate(pos + (x, 5, y), "000000"),
                cache[0][x, y, 3]
            ]
        for y in range(num_address_per_cache):
            cache_full_page_in[x, y] = LogicGate(
                pos + (x, 2, y+1), "FF0000", 1, xaxis=1, zaxis=-3)
            cache_full_page_out[x, y] = LogicGate(
                pos + (x, 2, y+num_address_per_cache+1), "0000FF", 1, xaxis=1, zaxis=-3)
    for x in range(bit_length):
        for y in range(banked_addresses):
            timer_bank[x, y, :] = [
                LogicGate(pos + (x*2 + bit_length, 7, y), "FF0000"),
                LogicGate(pos + (x*2 + bit_length+1, 7, y), "0000FF"),
                LogicGate(pos + (x*2 + bit_length, 8, y), "000000"),
                LogicGate(pos + (x*2 + bit_length+1, 8, y), "000000", 1),
                Timer(pos + (x*2 + bit_length, 9, y+1), "0000FF",
                      divmod(num_caches_per_bank-3, TICKS_PER_SECOND), xaxis=-3, zaxis=-2)
            ]
    for x in range(get_bits_required(num_timer_banks)):
        timer_bank_decoder_read_in[x, :] = [
            LogicGate(pos + (bit_length*3+1, 8, x),
                      "FF0000", 4, xaxis=1, zaxis=3),
            LogicGate(pos + (bit_length*3+2, 8, x),
                      "FF0000", 1, xaxis=1, zaxis=3),
        ]
        timer_bank_decoder_write_keep_in[x, :] = [
            LogicGate(pos + (bit_length*3+2, 6, x),
                      "FF0000", 4, xaxis=1, zaxis=3),
            LogicGate(pos + (bit_length*3+3, 6, x),
                      "FF0000", 1, xaxis=1, zaxis=3),
            LogicGate(pos + (bit_length*3+4, 6, x),
                      "FF0000", 4, xaxis=1, zaxis=3),
            LogicGate(pos + (bit_length*3+5, 6, x),
                      "FF0000", 1, xaxis=1, zaxis=3),
        ]
    for z in range(banked_addresses):
        timer_bank_decoder_write_keep[z, :] = [
            LogicGate(pos + (bit_length*3, 6, z), "000000", xaxis=1, zaxis=3),
            LogicGate(pos + (bit_length*3+1, 6, z),
                      "000000", 3, xaxis=1, zaxis=3),
        ]
    for x in range(get_bits_required(total_pages)):
        for z in range(num_caches):
            cache_table_lookup[x, z] = LogicGate(
                pos + (x-get_bits_required(total_pages) - 5, 5, z+1), "000000", 5, xaxis=1, zaxis=-3)

    connect(timer_bank[:, :, 4], timer_bank[:, :, 2])
    connect(timer_bank[:, :, 2], timer_bank[:, :, 3])
    connect(timer_bank[:, :, 3], timer_bank[:, :, 4])
    connect(timer_bank[:, :, 4], timer_bank[:, :, 1])
    connect(timer_bank[:, :, 0], timer_bank[:, :, 3])

    decoder(bp, banked_addresses,
            precreated_outputs=timer_bank_decoder_read,
            precreated_inputs_binary=timer_bank_decoder_read_in,
            precreated_output_enable=timer_bank_decoder_read_enable,
            address_divisor=num_address_per_cache)

    decoder(bp, banked_addresses,
            precreated_outputs=timer_bank_decoder_write_keep[:, 0],
            precreated_inputs_binary=timer_bank_decoder_write_keep_in[:, :2],
            precreated_output_enable=timer_bank_decoder_write_keep_enable[0],
            address_divisor=num_address_per_cache)

    decoder(bp, banked_addresses,
            precreated_outputs=timer_bank_decoder_write_keep[:, 1],
            precreated_inputs_binary=timer_bank_decoder_write_keep_in[:, 2:],
            precreated_output_enable=timer_bank_decoder_write_keep_enable[1],
            address_divisor=num_address_per_cache)

    connect(timer_bank_decoder_read, timer_bank[:, :, 1].T)
    connect(timer_bank_decoder_write_keep[:, 0], timer_bank[:, :, 0].T)
    connect(timer_bank_decoder_write_keep[:, 1], timer_bank[:, :, 2].T)

    for t, c in zip(timer_bank[:, :, 1].T, cycle(cache_full_page_in.T)):
        connect(t, c)

    for c, t in zip(cycle(cache_full_page_out.T), timer_bank[:, :, 0].T):
        connect(c, t)

    connect(cache_table[0][:, :, -1], cache_table_lookup)
    connect(cache_table[0][-2, :, -1], cache_table_lookup_dec)
    connect(cache_table_lookup_in, cache_table_lookup)
    connect(cache_table_lookup.T, cache_table_lookup_dec)
    connect(cache_table_lookup_dec, cache_table_lookup_out[-1])
    for x in range(num_caches):
        bit_mask = num_to_bit_list(
            x, get_bits_required(num_caches)+1)
        connect(cache_table_lookup_dec[x], cache_table_lookup_out[bit_mask])

    ram(bp,
        bit_length=bit_length*num_address_per_cache,
        num_address=cached_addresses,
        pos=pos + (0, 1, 0),
        address_divisor=num_address_per_cache,
        pre_arr=cache_arr,
        pre_inputs=cache_full_page_in.T.flat,
        pre_outputs=cache_full_page_out.T.flat)

    control_pos = pos+(0, 15, 0)
    data_register = register(bp, bit_length=bit_length, pos=control_pos)
    address_register = register(
        bp, bit_length=get_bits_required(total_bits//bit_length), pos=control_pos+(bit_length+1, 0, 0))
    read_write_register = register(
        bp, bit_length=1, pos=control_pos+(bit_length+get_bits_required(total_bits//bit_length)+2, 0, 0))
    execute = LogicGate(pos=control_pos+(bit_length+get_bits_required(total_bits//bit_length)+3, 3, 0),
                        color="FF0000",
                        controller=1)
    execution_done = LogicGate(pos=control_pos+(bit_length+get_bits_required(total_bits//bit_length)+4, 3, 0),
                               color="0000FF",
                               controller=1)

    address_comparator = [
        # cache_table
        [LogicGate(pos + (-get_bits_required(total_pages) - 5 + x, 8, num_caches),
                   "000000",
                   5, xaxis=1, zaxis=3) for x in range(get_bits_required(num_caches_per_bank))],
        LogicGate(pos + (-get_bits_required(total_pages) - 5, 8, num_caches+1),
                  "000000", 0, xaxis=1, zaxis=3),
    ]
    connect(address_comparator[0], address_comparator[1])
    connect(clock[:, 0], address_comparator[0])
    connect(cache_table[2], address_comparator[0])

    row_start = control_pos+(-1, -1, 0)

    selectors = [
        [LogicGate(row_start+(x,5,0), "000000") for x in range(get_bits_required(total_pages))],
        [Timer(row_start+(x,6,0), "000000", (0,2)) for x in range(get_bits_required(total_pages))],
        [LogicGate(row_start+(x,7,0), "000000") for x in range(get_bits_required(total_pages))],
        [LogicGate(row_start+(x,8,0), "000000") for x in range(get_bits_required(num_caches))],
        # [Timer(row_start+(x,6,0), "000000", (0,0)) for x in range(get_bits_required(num_caches))],
        # [LogicGate(row_start+(x,7,0), "000000") for x in range(get_bits_required(num_caches))],
    ]
    connect(address_register[0][::-1, 1], selectors[0][::-1])
    connect(selectors[0], cache_table[1])
    connect(cache_table[2], selectors[1])
    connect(selectors[1], selectors[2])
    connect(selectors[2], cache_table[1])
    connect(cache_table_lookup_out, selectors[3])
    connect(selectors[3], cache_table[3])

    connect(address_register[0][::-1, 1], cache_table_lookup_in[::-1])
    connect(cache_table_lookup_out[-2::-1], cache[3][::-1])
    connect(cache_table_lookup_out[-2::-1], cache[6][::-1])
    connect(address_register[0][:get_bits_required(
        num_address_per_cache), 1], cache[3])
    connect(address_register[0][:get_bits_required(
        num_address_per_cache), 1], cache[6])
    connect(cache[2], data_register[0][:, -1])
    connect(data_register[0][:, 1], cache[1])
    connect(address_register[0][get_bits_required(
        num_address_per_cache):, 1], cache_table[1])
    # connect(cache_table_lookup_out, cache_table[3])
    connect(cache_pointer[0][:, 0], cache_table[6])

    def NODE(t=0, x=0, y=0, z=0, _from=[], _to=[]):
        if t == 6:
            g = LogicGate(row_start+(-x, y, z), "000000", 2, xaxis=-1, zaxis=2)
            connect(g, g)
        else:
            g = LogicGate(row_start+(-x, y, z), "000000", t, xaxis=-1, zaxis=2)
        connect(_from, g)
        connect(g, _to)
        bp.add(g)
        return g

    g0 = NODE(x=0, _from=execute)
    g1 = NODE(x=1, _from=g0, )
    g2 = NODE(x=2, _from=g1, )
    g3 = NODE(x=3, _from=g2, )
    g4 = NODE(x=4, _from=g3, )
    g5 = NODE(x=5, _from=g4, )
    # If (page loaded)
    g6 = NODE(x=6, _from=(g5), )
    g7 = NODE(x=6, y=1, _from=(cache_table_lookup_out[-1]), )
    g8 = NODE(x=6, y=2, t=3, _from=(cache_table_lookup_out[-1]), )
    # Then:
    g9 = NODE(x=7, _from=(g6, g7), )
    #   If (read mode)
    g10 = NODE(x=8, t=1, _from=(g9), _to=(
        cache_table[1][-1], cache_table[1][-2], cache_table[5]))
    g11 = NODE(x=8, y=1, _from=(read_write_register[0][:, 1]), )
    g12 = NODE(x=8, y=2, t=3, _from=(read_write_register[0][:, 1]), )
    #   Then:
    g13 = NODE(x=9, _from=(g10, g11), _to=(cache[8]))
    g14 = NODE(x=10, _from=(g13))
    g15 = NODE(x=11, _from=(g14))
    g16 = NODE(x=12, _from=(g15))
    g17 = NODE(x=13, _from=(g16), _to=(data_register[1], execution_done))
    #   Else:
    g18 = NODE(x=9, y=2, _from=(g10, g12), _to=(cache[5], execution_done))
    # Else:
    g19 = NODE(x=6, y=3, _from=(g6, g8))
    # g20 = NODE(x=6, y=4, t=1, _from=(g19), _to=(cache_table[8]))
    # g21 = NODE(x=7, y=4, _from=(g20))
    # g22 = NODE(x=8, y=4, _from=(g21))
    # g23 = NODE(x=9, y=4, _from=(g22))
    # g24 = NODE(x=10, y=4, _from=(g23))
    # #   If (Invalid page)
    # g25 = NODE(x=11, y=4, _from=(g24))
    # g26 = NODE(x=11, y=5, _from=(cache_table[2][-2]))
    # g27 = NODE(x=11, y=6, t=3, _from=(cache_table[2][-2]))
    # #   Then:
    # g28 = NODE(x=12, y=4, _from=(g25, g27), _to=(selectors[0]))
    # g29 = NODE(x=13, y=4, _from=(g28), _to=(
    #     cache_table[1][-1], cache_table[1][-2], cache_table[5]))
    # g30 = NODE(x=14, y=4, _from=(g29))
    # g30_1 = NODE(x=15, y=4, _from=(g30), _to=(g10))
    # #   Else:
    # #       If (Visited bit set)
    # g31 = NODE(x=12, y=6, _from=(g25, g26))
    # g31_1 = NODE(x=11, y=8, _from=(cache_table[2][-1]))
    # g32 = NODE(x=12, y=7, _from=(g31_1))
    # g33 = NODE(x=12, y=8, t=3, _from=(g31_1))
    # #       Then:
    # g34 = NODE(x=13, y=6, _from=(g31, g32), _to=(selectors[2], cache_pointer[1]))
    # g35 = NODE(x=14, y=6, _from=(g34), _to=(cache_table[1][-2], cache_table[5]))


    bp.add(cache_arr[:, :, :3], cache_full_page_in, cache_full_page_out,
           timer_bank, timer_bank_decoder_read, timer_bank_decoder_read_in, timer_bank_decoder_read_enable,
           timer_bank_decoder_write_keep, timer_bank_decoder_write_keep_in, timer_bank_decoder_write_keep_enable,
           cache_table_lookup, cache_table_lookup_in, cache_table_lookup_out, cache_table_lookup_dec,
           execute, execution_done, address_comparator, selectors)

    print(
        f"Total memory: {total_bits/8} bytes, "
        f"Cached memory: {cached_bits/8} bytes, ")

    # timers = ndarray((bit_length, 3), dtype=object)
    # timer_read_write_enable = LogicGate(pos + (-1, 1, 0), "FF0000", 4)
    # for x in range(bit_length):
    #     # timers[x] = [
    #     #     t0 := Timer(pos + (x % 8, 0, 2*(x//8)), "000000", ((num_address-3) // 40, (num_address-3) % 40)),
    #     #     l0 := LogicGate(pos + (x % 8, 1, 2*(x//8)), "000000"),
    #     #     l1 := LogicGate(pos + (x % 8, 1, 2*(x//8)+1), "000000", 1),
    #     # ]
    #     timers[x] = [
    #         t0 := Timer(pos + (x, 0, 0), "000000", ((num_address_per_cache-3) // 40, (num_address_per_cache-3) % 40)),
    #         l0 := LogicGate(pos + (x, 1, 0), "000000"),
    #         l1 := LogicGate(pos + (x, 1, 1), "000000", 1),
    #     ]
    #     t0.connect(l0).connect(l1).connect(t0)
    # connect(timer_read_write_enable, timers[:, 1])

    # for z in range(num_caches):
    #     cpos = pos + (0, 0, z*2)
    #     data = register(bp, bit_length, pos=cpos + (0, 4, 0))
    #     timers_readers = [LogicGate(cpos+(x, 3, 0), "000000")
    #                       for x in range(bit_length)]
    #     timers_readers_enable = LogicGate(cpos+(-1, 3, 0), "FF0000", 1)
    #     timers_readers_buffer = LogicGate(cpos+(-1, 5, 0), "000000")
    #     address = register(bp, get_bits_required(
    #         num_address_per_cache), pos=cpos + (bit_length+1, 5, 0), OE=False)
    #     post_rw = register(bp, 2,
    #                        pos=cpos + (bit_length+1+get_bits_required(num_address_per_cache)+1, 5, 0), OE=False)
    #     rw_inv = [
    #         LogicGate(
    #             cpos + (bit_length+1+get_bits_required(num_address_per_cache)+1, 4, 0), "000000", 3),
    #         LogicGate(
    #             cpos + (bit_length+1+get_bits_required(num_address_per_cache)+2, 4, 0), "000000")
    #     ]
    #     comparator = [LogicGate(cpos+(x+bit_length+1, 4, 0), "000000", 5)
    #                   for x in range(get_bits_required(num_address_per_cache))]
    #     comparator_write = LogicGate(cpos+(bit_length+1, 3, 0), "000000")
    #     comparator_read = LogicGate(cpos+(bit_length+2, 3, 0), "000000")
    #     connect(post_rw[0][0, 0], rw_inv)
    #     connect(address[0][:, 0], comparator)
    #     connect(clock[:, 0], comparator)
    #     connect(comparator, comparator_write)
    #     connect(comparator, comparator_read)
    #     connect(rw_inv[0], comparator_write)
    #     connect(rw_inv[1], comparator_read)
    #     connect(post_rw[0][1, 0], comparator_write)
    #     connect(post_rw[0][1, 0], comparator_read)
    #     connect(comparator_write, timer_read_write_enable)
    #     connect(comparator_write, data[2])
    #     connect(data[0][:, 0], timers[:, 2])
    #     connect(comparator_write, post_rw[1])
    #     connect(comparator_read, post_rw[1])
    #     connect(comparator_read, timers_readers_enable)
    #     connect(timers_readers_enable, timers_readers_buffer)
    #     connect(timers_readers_buffer, data[1])
    #     connect(timers_readers_enable, timers_readers)
    #     connect(timers[:, 0], timers_readers)
    #     connect(timers_readers, data[0][:, 3])
    #     bp.add(comparator, comparator_write, comparator_read, rw_inv,
    #            timers_readers, timers_readers_enable, timers_readers_buffer)

    # bp.add(timers, timer_read_write_enable)

    # print(f"Timer ram: {bit_length*num_address_per_cache} bits ({bit_length*num_address_per_cache/8} bytes), "
    #       f"Max time delay: {
    #           num_address_per_cache} ticks ({num_address_per_cache/40} seconds), "
    #       f"Bits per part: {bit_length*num_address_per_cache / (len(bp.bodies[0].childs)-initial_part_count):.2f} bits/part")
