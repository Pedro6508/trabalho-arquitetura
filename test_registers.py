import unittest
import random as r
import registers as reg
import arithmetic as arith

class MyTestCase(unittest.TestCase):
    def test_conversion(self):
        attemps = 10
        wordsize = 32
        for _ in range(0, attemps):
            magnitude = 2 ** (r.randint(0, wordsize))
            value = r.randint(0, magnitude)

            arr = reg.toArr_aux(value)
            num_arr = reg.toNum_aux(arr)

            self.assertEqual(value, num_arr)


    def test_full_adder_32bits(self):
        attemps = 10
        wordsize = 33
        overflow = 2**wordsize
        for _ in range(0, attemps):
            magnitude = 2 ** (r.randint(0, wordsize))
            random_code = r.randint(0, 0b11 + 1)
            code_x_num = random_code
            code_y_num = code_x_num ^ 0b11

            value_x = r.randint(0, magnitude)
            code_x = reg.toArr_aux(code_x_num)
            data_x = reg.toArr_aux(value_x)

            value_y = r.randint(0, magnitude)
            code_y = reg.toArr_aux(code_y_num)
            data_y = reg.toArr_aux(value_y)

            reg.write_register(code_x, data_x)
            reg.write_register(code_y, data_y)

            sum_reg = arith.full_adder_32bits(code_x, code_y)

            sum_comp = value_x + value_y
            carry_comp = (sum_comp & overflow) >> wordsize
            result_comp = sum_comp & (overflow - 1)

            self.assertEqual(result_comp, reg.toNum_aux(sum_reg["result"]))
            self.assertEqual(carry_comp, sum_reg["carry"])

            zero = reg.toArr_aux(0)

            reg.write_register(code_x, zero)
            reg.write_register(code_y, zero)


if __name__ == '__main__':
    unittest.main()
