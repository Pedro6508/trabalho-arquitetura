import sys

fsrc = open(str(sys.argv[1]), 'r')

lines = []
lines_bin = []
names = []

instructions = ['add', 'sub', 'goto', 'mov', 'jz', 'halt', 'wb', 'ww']
instruction_set = {'add' : 0x02, 
                   'sub' : 0x06, 
                   'mov' : 0x0A, 
                   'goto': 0x0D,
                   'jz'  : 0x0F, 
                   'halt': 0xFF}
   
   
   
def is_instruction(str):
   global instructions
   inst = False
   for i in instructions:
      if i == str:
         inst = True
         break
   return inst
   
def is_name(str):
   global names
   name = False
   for n in names:
      if n[0] == str:
         name = True
         break
   return name

# mandatory ops:
#  h = x + h {
#  reg_num = 3
#  alu = 00111100
#  
# }
#  y -> result 
#  x -> input
#  x = y + h
#  name + name 
   
def encode_2ops(inst, ops):
   line_bin = []
   if len(ops) > 1:
      if ops[0] == 'x':
         if is_name(ops[1]):
            line_bin.append(instruction_set[inst])
            line_bin.append(ops[1])
   return line_bin

def encode_goto(ops):
   line_bin = []
   if len(ops) > 0:
      if is_name(ops[0]):
         line_bin.append(instruction_set['goto'])
         line_bin.append(ops[0])
   return line_bin
   
def encode_halt():
   line_bin = []
   line_bin.append(instruction_set['halt'])
   return line_bin
   
def encode_wb(ops):
   line_bin = []
   if len(ops) > 0:
      if ops[0].isnumeric():
         if int(ops[0]) < 256:
            line_bin.append(int(ops[0]))
   return line_bin   

def encode_ww(ops):
   line_bin = []
   if len(ops) > 0:
      if ops[0].isnumeric():
         val = int(ops[0])
         if val < pow(2,32):
            line_bin.append(val & 0xFF)
            line_bin.append((val & 0xFF00) >> 8)
            line_bin.append((val & 0xFF0000) >> 16)
            line_bin.append((val & 0xFF000000) >> 24)
   return line_bin
      
def encode_instruction(inst, ops):
   if inst == 'add' or inst == 'sub' or inst == 'mov' or inst == 'jz':
      return encode_2ops(inst, ops)
   elif inst == 'goto':
      return encode_goto(ops)
   elif inst == 'halt':
      return encode_halt()
   elif inst == 'wb':
      return encode_wb(ops)
   elif inst == 'ww':
      return encode_ww(ops)
   else:
      return []
   
# firmware[17:255] -> free 
def make_add_firmware(inst, ops):
   ALU = 00111100 # H + Reg
   h = 0
   b = 0

      
   
def line_to_bin_step1(line):
   line_bin = []
   if is_instruction(line[0]):
      line_bin = encode_instruction(line[0], line[1:])
   else:
      line_bin = encode_instruction(line[1], line[2:])
   return line_bin
   
def lines_to_bin_step1():
   global lines
   for line in lines:
      line_bin = line_to_bin_step1(line)
      if line_bin == []:
         print("Erro de sintaxe na linha ", lines.index(line))
         return False
      lines_bin.append(line_bin)
   return True

def find_names():
   global lines
   for k in range(0, len(lines)):
      is_label = True
      for i in instructions:
          if lines[k][0] == i:
             is_label = False
             break
      if is_label:
         names.append((lines[k][0], k))
         
def count_bytes(line_number):
   line = 0
   byte = 1
   while line < line_number:
      byte += len(lines_bin[line])
      line += 1
   return byte

def get_name_byte(str):
   for name in names:
      if name[0] == str:
         return name[1]
         
def resolve_names():
   for i in range(0, len(names)):
      names[i] = (names[i][0], count_bytes(names[i][1]))
   for line in lines_bin:
      for i in range(0, len(line)):
         if is_name(line[i]):
            if line[i-1] == instruction_set['add'] or line[i-1] == instruction_set['sub'] or line[i-1] == instruction_set['mov']:
               line[i] = get_name_byte(line[i])//4
            else:
               line[i] = get_name_byte(line[i])

for line in fsrc:
   tokens = line.replace('\n','').replace(',','').lower().split(" ")
   i = 0
   while i < len(tokens):
      if tokens[i] == '':
         tokens.pop(i)
         i -= 1
      i += 1
   if len(tokens) > 0:
      lines.append(tokens)
   
find_names()
if lines_to_bin_step1():
   resolve_names()
   byte_arr = [0]
   for line in lines_bin:
      for byte in line:
         byte_arr.append(byte)
   fdst = open(str(sys.argv[2]), 'wb')
   fdst.write(bytearray(byte_arr))
   fdst.close()

fsrc.close()