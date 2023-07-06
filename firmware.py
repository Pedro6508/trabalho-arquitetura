from array import array

ARCH = 32

FIRMWARE = dict()


def architecture_setup():
    global ARCH, FIRMWARE

    FIRMWARE[0] = new_instruction(
        goto=[0] * 9,
        jump=[1, 0, 0],
        arith_operation=[0, 0],
        arith_control=[1, 1],
        arith_out=[0, 1],
        arith_shift=[0, 1],
        write_out=[0, 0],
        read_a=[1, 0],
        read_b=[0, 0],
    )

    assert FIRMWARE[0] == array_from_int(
        0b000_000_000_100_00_11_01_01_00_10_00
    )


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
    assert type(instruction) == object

    instruction.next_addr.set(goto)
    assert len(goto) == instruction.next_addr.size

    instruction.jump.set(jump)
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

    instruction.alu.set(
        arith_operation +
        arith_control +
        arith_out +
        arith_shift
    )
    assert len(alu_compose) == instruction.alu.size

    instruction.c.set(write_out)
    assert len(write_out) == instruction.c.size

    bus_compose = (
            read_a +
            read_b
    )
    assert len(read_a) == 2
    assert len(read_b) == 2

    instruction.bus.set(bus_compose)
    assert len(bus_compose) == instruction.bus.size

    return instruction


def get_instruction(index: int) -> [int]:
    global FIRMWARE

    if index in FIRMWARE:
        return FIRMWARE[index]
    else:
        FIRMWARE[index] = Instruction()
        return FIRMWARE[index]


def new_obj(name, data):
    return type(name, (object,), data)()


class Instruction(object):
    class Signal(object):
        size: int
        start: int
        stop: int
        data: list

        def __int__(self, size: int, start: int):
            self.size = size
            self.start = start
            self.stop = start + size

            self.data = instruction.data[
                slice(
                    start=start,
                    stop=self.stop
                )
            ]

            return self

        def code(self):
            return self.instruction.data[
                slice(
                    start=start,
                    stop=self.stop
                )
            ]

        def set(self, value: [int]):
            for i, (_, bit) in enumerate(zip(self.data, value)):
                self.instruction.data[
                    i + self.start
                    ] = bit

    data: [int]
    next_addr: Signal
    jump: Signal
    alu: Signal
    c: Signal
    bus: Signal

    def __int__(self):
        # global new_obj
        self.data = array('B', [0]) * ARCH

        self.next_addr = Singnal(
            instruction=self,
            size=9,
            start=0,
        )

        self.jump = Singnal(
            instruction=self,
            size=3,
            start=self.next_addr.stop,
        )

        self.alu = Singnal(
            instruction=self,
            size=8,
            start=self.jump.stop,
        )

        self.c = Signal(
            instruction=self,
            size=9,
            start=self.alu.stop
        )

        self.bus = Signal(
            instruction=self,
            size=4,
            start=self.alu.stop
        )

        return self


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
