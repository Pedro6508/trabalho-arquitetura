import random as r
import unittest

import arithmetic as arith
import firmware
import registers as reg


def rand_bin(size: int, log_compensation=True) -> int:
    # python randint(a,b) é inclusivo para a e b.

    if log_compensation == True:
        rand_log = r.randint(0, size)
        max_value = 2 ** rand_log
    else:
        max_value = 2 ** size

    inclusive_max_value = max_value - 1
    return r.randint(0, inclusive_max_value)


class MyTestCase(unittest.TestCase):
    def test_conversion(self):
        attempts = 10
        word_size = 32
        for _ in range(0, attempts):
            value = rand_bin(word_size)

            arr = firmware.array_from_int(value)
            num_arr = firmware.int_from_array(arr)

            self.assertEqual(value, num_arr)

    def debug_arith_mask(self):
        word_size = 1
        while word_size < firmware.ARCH:
            mask = arith.mask_aux(word_size)
            word_size = word_size << 1

        self.assertEqual(0, 0)

    def test_basic_arith(self):
        word_size = 3
        max_bin = 2 ** word_size
        for i in range(0, max_bin):
            for j in range(0, max_bin):
                i_1bit = i & 0b1
                i_2bits = (i & 0b10) >> 1

                j_1bit = j & 0b1
                j_2bits = (j & 0b10) >> 1

                sum_half = i_1bit + j_1bit
                s_half = sum_half & 0b1
                c_half = (sum_half & 0b10) >> 1

                self.assertEqual(
                    {
                        's': s_half,
                        'c': c_half
                    },
                    arith.half_adder_aux(
                        i_1bit,
                        j_1bit
                    )
                )

                c_in = i_1bit ^ j_1bit  # c_in == 1 em 50% dos casos
                sum_full = i_1bit + j_1bit + c_in
                s_full = sum_full & 0b1
                c_out_full = (sum_full & 0b10) >> 1

                self.assertEqual(
                    {
                        's': s_full,
                        'c_out': c_out_full
                    },
                    arith.full_adder_1bit_aux(
                        a=i_1bit,
                        b=j_1bit,
                        c_in=c_in
                    )
                )

                self.assertEqual(
                    i_2bits * j_2bits,
                    arith.mult_2bits_aux(i_2bits, j_2bits)
                )

    def test_full_adder_32bits(self):
        attempts = 100
        word_size = 32
        overflow = 2 ** word_size
        for _ in range(0, attempts):
            inclusive_max_code = reg.REG_TYPE - 1
            random_code = rand_bin(inclusive_max_code)
            code_x_num = random_code | reg.REG_TYPE
            code_y_num = code_x_num ^ reg.REG_MASK

            value_x = rand_bin(word_size)
            code_x = firmware.array_from_int(code_x_num)
            data_x = firmware.array_from_int(value_x)

            value_y = rand_bin(word_size)
            code_y = firmware.array_from_int(code_y_num)
            data_y = firmware.array_from_int(value_y)

            reg.write_register(code_x, data_x)
            reg.write_register(code_y, data_y)

            sum_reg = arith.full_adder_32bits(code_x, code_y)

            sum_comp = value_x + value_y
            carry_comp = (sum_comp & overflow) >> word_size
            carry_reg = sum_reg["carry"]

            result_comp = (sum_comp | overflow) ^ overflow
            result_reg = firmware.int_from_array(sum_reg["result"])

            zero = firmware.array_from_int(0)

            self.assertEqual(result_comp, result_reg)
            self.assertEqual(carry_comp, carry_reg)

            reg.write_register(code_x, zero)
            reg.write_register(code_y, zero)


if __name__ == '__main__':
    unittest.main()
