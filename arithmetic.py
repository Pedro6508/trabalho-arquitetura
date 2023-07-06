from array import array

import firmware
import registers as reg

get_ZERO = lambda size: array('B', [0]) * size   # Zero não é registrador

get_ARR = lambda: reg.read_register(
            firmware.array_from_int(reg.ARR_CODE)
)

set_ARR = lambda DATA: reg.write_register(
    firmware.array_from_int(reg.ARR_CODE),
    DATA
)

clean_ARR = lambda: set_ARR(
    get_ZERO(reg.ARR_SIZE)
)

def mult_32_bits(reg_code_x: [int], reg_code_y: [int]):
    global get_ARR, get_ZERO, clean_ARR
    reg_x = reg.read_register(reg_code_x)
    reg_y = reg.read_register(reg_code_y)

    ARR = get_ARR()

    return 0



def full_adder_32bits(reg_code_x: [int], reg_code_y: [int]):
    reg_x = reg.read_register(reg_code_x)
    reg_y = reg.read_register(reg_code_y)

    carry = get_ZERO(firmware.ARCH + 1)
    result = get_ZERO(firmware.ARCH)

    for i in range(0, firmware.ARCH):
        res = full_adder_1bit_aux(
            a=reg_x[i],
            b=reg_y[i],
            c_in=carry[i]
        )

        result[i] = res['s']
        carry[i+1] = res['c_out']

    last_carry_bit = carry[len(carry)-1]

    return {
        "result": result,
        "carry": last_carry_bit
    }


# Metodos Auxiliares


def mask_aux(mod_mask: int, size=None):
    global get_ZERO
    if size is None:
        size = firmware.ARCH

    mask = get_ZERO(size)

    for i in range(0, size):
        if i & mod_mask == 0:
            mask[i] = 1

    return mask


def shift_aux(arr: [int], shift_size: int, shift_num: int):
    shift_size00 = shift_size & 0b11
    shift_num00 = shift_num & 0b11

    total_shift = shift_size00*shift_num00

    for i, bit in enumerate(arr):
        shifted_i = i + total_shift
        if shifted_i < len(arr):
            arr[shifted_i] = bit
        else:
            arr[i] = 0

    return arr



def mult_2bits_aux(a: int, b: int):
    a0 = a & 0b01
    a1 = (a & 0b10) >> 1

    b0 = b & 0b01
    b1 = (b & 0b10) >> 1

    and_ab_00 = a0 & b0
    and_ab_01 = a0 & b1
    and_ab_10 = a1 & b0
    and_ab_11 = a1 & b1

    sum_0 = half_adder_aux(
        a=and_ab_10,
        b=and_ab_01
    )

    sum_1 = half_adder_aux(
        a=sum_0['c'],
        b=and_ab_11
    )

    p00 = and_ab_00
    p01 = sum_0['s']
    p10 = sum_1['s']
    p11 = sum_0['c']

    result = (p11 << 3) + (p10 << 2) + (p01 << 1) + p00

    return result


def half_adder_aux(a: int, b: int):
    a0 = a & 0b1
    b0 = b & 0b1

    s = a0 ^ b0
    c = a0 & b0

    return {
        's': s,
        'c': c
    }


def full_adder_1bit_aux(a: int, b: int, c_in):
    a0 = a & 0b1
    b0 = b & 0b1
    c_in0 = c_in & 0b1

    half_a_1 = half_adder_aux(
        a=a0,
        b=b0
    )

    half_a_2 = half_adder_aux(
        a=half_a_1['s'],
        b=c_in0
    )

    s = half_a_2['s']
    c_out = half_a_1['c'] | half_a_2['c']

    return {
        's': s,
        'c_out': c_out
    }