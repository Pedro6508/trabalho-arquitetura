from array import array
from copy import copy

from firmware import ARCH, int_from_array

ARCH_MASK = (2 ** ARCH) - 1

ARR_CODE = 0b00
MAR_CODE = 0b01
MDR_CODE = 0b10

ARR_SIZE = ARCH << 2
REG_MASK = 0b11
REG_TYPE = 0b100

ARCH_ARRAY = lambda: array('B', [0]) * ARCH

REGISTERS = {
    'r0': ARCH_ARRAY(),
    'r1': ARCH_ARRAY(),
    'r2': ARCH_ARRAY(),
    'r3': ARCH_ARRAY(),

    'AAR': array('B', [0]) * ARR_SIZE,  # Auxiliary Arithmetic Register

    'MAR': ARCH_ARRAY(),  # Memory Address Register
    'MDR': ARCH_ARRAY(),  # Memory Data Register

    'MIR': ARCH_ARRAY()  # Memory Instruction Register
}


def write_register(reg_code: [int], data: [int], path=None):
    if path is None:
        reg_path = demux_register(reg_code)
    else:
        reg_path = path

    for i, bit in enumerate(data):
        REGISTERS[reg_path][i] = bit


def read_register(reg_code: [int], path=None) -> [int]:
    if path is None:
        reg_path = demux_register(reg_code)
    else:
        reg_path = path

    return copy(REGISTERS[reg_path])  # copy para evitar atribuicao de valor com read


# Metodos Auxiliares

def demux_register(reg_code: [int]) -> [int]:
    global REGISTERS, REG_TYPE, REG_MASK


    code_raw = int_from_array(reg_code) & 0b111
    if code_raw & REG_TYPE == REG_TYPE:
        # Proposito Geral
        reg_path = "r" + str(code_raw & REG_MASK)
    else:
        # Proposito Especifico
        if code_raw & REG_MASK == ARR_CODE:
            reg_path = 'AAR'
        elif code_raw & REG_MASK == MAR_CODE:
            reg_path = 'MAR'
        elif code_raw & REG_MASK == MDR_CODE:
            reg_path = 'MDR'
        else:
            reg_path = '----'

    return reg_path
