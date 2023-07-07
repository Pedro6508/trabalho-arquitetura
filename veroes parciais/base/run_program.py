import sys

import clock as clk
import disk
import memory as mem
import ufc2x as cpu

disk.read(str(sys.argv[1]))

clk.start([cpu])

print("Depois: ", mem.read_word(1))