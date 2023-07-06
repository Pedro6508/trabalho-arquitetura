from array import array
import registers as reg


def full_adder_32bits(reg_code_x: [int], reg_code_y: [int]):
    reg_x = reg.read_register(reg_code_x)
    reg_y = reg.read_register(reg_code_y)

    carry = 0
    result = array('B', [0]) * reg.ARCH

    for i in range(0, reg.ARCH):
        res = full_adder_1bit_aux(
            a=reg_x[i],
            b=reg_y[i],
            c_in=carry
        )

        carry = res['c_out']
        result[i] = res['s']

    return {
        "result": result,
        "carry": carry
    }


def shift_aux(arr: [int], shift_size: int, shift_num: int):
    shift_size = shift_size & 0b11
    shift_num = shift_num & 0b11

    total_shift = shift_size*shift_num

    for i,bit in enumerate(arr):
        shifted_i = i + total_shift
        if shifted_i < len(arr):
            arr[shifted_i] = bit
        else:
            arr[i] = 0

    return arr


# Metodos Auxiliares


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

    result = {}


def half_adder_aux(a: int, b: int):
    a = a & 0b1
    b = b & 0b1

    s = a ^ b
    c = a & b

    return {
        's': s,
        'c': c
    }


def full_adder_1bit_aux(a: int, b: int, c_in):
    a = a & 0b1
    b = b & 0b1
    c_in = c_in & 0b1

    half_a_1 = half_adder_aux(
        a=a,
        b=b
    )

    half_a_2 = half_adder_aux(
        a=half_a_1['s'],
        b=c_in
    )

    s = half_a_2['s']
    c_out = half_a_1['c'] | half_a_2['c']

    return {
        's': s,
        'c_out': c_out
    }