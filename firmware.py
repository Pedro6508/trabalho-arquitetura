from array import array

ARCH = 32

FIRMWARE = dict()


def architecture_setup():
    global ARCH, FIRMWARE

    FIRMWARE[0] = new_instruction(
        goto=[0] * 9,

        jump=[1, 0, 0],

        arith_operation=[0, 0],
        arith_control=[1, 1, 0],
        arith_out=[1],
        arith_shift=[0, 1],

        write_out=[0] * 9,

        read_a=[1, 0],
        read_b=[0, 0],
    )

    arr = array('B', [0] * 9 + [1, 0, 0] + [0, 0] + [1, 1, 0] + [1] + [0, 1] + ([0] * 9) + [1, 0] + [0])  # ajustar

    print(FIRMWARE[0].arr)
    print(arr)
    print(FIRMWARE[0].alu.get_code())
    print(FIRMWARE[0].c.get_code())
    print(FIRMWARE[0].bus.get_code())

    assert FIRMWARE[0].arr == arr


def new_instruction(
        goto: [int],

        jump: [int],

        arith_operation: [int],
        arith_control: [int],
        arith_out: [int],
        arith_shift: [int],

        write_out: [int],

        read_a: [int],
        read_b: [int],
):
    instruction = Instruction()
    instruction.__int__()

    instruction.next_addr.set_code(goto)
    assert len(goto) == instruction.next_addr.size

    instruction.jump.set_code(jump)
    assert len(jump) == instruction.jump.size

    alu_compose = (
            arith_operation +
            arith_control +
            arith_out +
            arith_shift
    )
    assert len(arith_operation) == 2
    assert len(arith_control) == 3
    assert len(arith_out) == 1
    assert len(arith_shift) == 2

    instruction.alu.set_code(
        alu_compose
    )
    assert len(alu_compose) == instruction.alu.size

    instruction.c.set_code(write_out)
    assert len(write_out) == instruction.c.size

    bus_compose = (
            read_a +
            read_b
    )
    assert len(read_a) == 2
    assert len(read_b) == 2

    instruction.bus.set_code(bus_compose)
    assert len(bus_compose) == instruction.bus.size

    return instruction


def get_instruction(index: int) -> [int]:
    global FIRMWARE

    if index in FIRMWARE:
        return FIRMWARE[index]
    else:
        FIRMWARE[index] = Instruction
        return FIRMWARE[index]


def array_from_int(value: int, word_type=0, word_size=None) -> [int]:
    word_type00 = word_type & 0b11
    if word_size is None:
        word_size = ARCH >> word_type00

    arr = array('B', [0]) * word_size

    bin_str = bin(value)[2:]
    last_bit = min(len(bin_str), word_size) - 1

    for i, bit in enumerate(bin_str):
        arr[last_bit - i] = int(bit)

    return arr


def int_from_array(arr: [int]) -> int:
    num = 0
    for i, _ in enumerate(arr):
        num += arr[i] * (2 ** i)

    return num


# noinspection PyTypeChecker
class Instruction:
    def __int__(self):
        self.arr = array('B', [0]) * ARCH

        self.next_addr = Signal()
        self.next_addr.ins_data = self.arr
        self.next_addr.size = 9
        self.next_addr.start = 0
        self.next_addr.arr = self.arr[
            slice(self.next_addr.start, self.next_addr.get_stop())
        ]

        self.jump = Signal()
        self.jump.ins_data = self.arr
        self.jump.size = 3
        self.jump.start = self.next_addr.get_stop()
        self.jump.arr = self.arr[
            slice(self.jump.start, self.jump.get_stop())
        ]

        self.alu = Signal()
        self.alu.ins_data = self.arr
        self.alu.size = 8
        self.alu.start = self.jump.get_stop()
        self.alu.arr = self.arr[
            slice(self.alu.start, self.alu.get_stop())
        ]

        self.c = Signal()
        self.c.ins_data = self.arr
        self.c.size = 9
        self.c.start = self.alu.get_stop()
        self.c.arr = self.arr[
            slice(self.c.start, self.c.get_stop())
        ]

        self.bus = Signal()
        self.bus.ins_data = self.arr
        self.bus.size = 4
        self.bus.start = self.c.get_stop()
        self.bus.arr = self.arr[
            slice(self.bus.start, self.bus.get_stop())
        ]


class Signal:
    stop: None or int
    start: None or int
    size: None or int
    ins_data: None or [int]

    def get_stop(self):
        self.stop = self.size + self.start
        return self.stop

    def get_code(self):
        return self.ins_data[
            slice(self.start, self.stop)
        ]

    def set_code(self, value: [int]):
        for i, (_, bit) in enumerate(zip(self.get_code(), value)):
            self.ins_data[
                i + self.start
                ] = bit
