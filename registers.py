from array import array

ARCH = 32

REGISTERS = {
    'r0': array('B', [0]) * ARCH,
    'r1': array('B', [0]) * ARCH,
    'r2': array('B', [0]) * ARCH,
    'r3': array('B', [0]) * ARCH
}


def write_register(reg_code: [int], data: [int]):
    global REGISTERS
    code_num = toNum_aux(reg_code) & 0b11
    reg_path = "r" + str(code_num)

    for i, bit in enumerate(data):
        REGISTERS[reg_path][i] = bit


def read_register(reg_code: [int]):
    global REGISTERS
    code_num = toNum_aux(reg_code) & 0b11
    reg_path = "r" + str(code_num)

    return REGISTERS[reg_path]

# Metodos Auxiliares

def toArr_aux(value: int, word_size=0):
    global ARCH
    word_size = word_size & 0b11
    arr = array('B', [0]) * (ARCH >> word_size)

    binStr = bin(value)[2:]
    last_bit = min(len(binStr), len(arr)) - 1
    for i, bit in enumerate(binStr):
        arr[last_bit - i] = int(bit)

    return arr


def toNum_aux(arr: [int]):
    num = 0
    for i, _ in enumerate(arr):
        num += arr[i] * (2 ** i)

    return num
