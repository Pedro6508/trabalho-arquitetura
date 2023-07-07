from firmware import FIRMWARE, int_from_array, array_from_int
import registers as reg

def alu():
    firm_addr = int_from_array(reg.REGISTERS['MIR'])

    alu_signal = FIRMWARE[firm_addr].alu.get_code()

    arith_operation = alu_signal[:2]
    arith_control = alu_signal[2:5]
    arith_out = alu_signal[5:7]
    arith_shift = alu_signal[7:9]

    if arith_operation == [0, 0]:
        op_or = 1
    elif arith_operation == [0, 1]:
        op_and = 1
    elif arith_operation == [1, 0]:
        op_sum = 1
    else:
        op_mult = 1

    if arith_control[0] == 1:
        enb_A = 1

    if arith_control[1] == 1:
        enb_B = 1

    if arith_control[2] == 1
        

    if arith_cont
        enb_B = 1