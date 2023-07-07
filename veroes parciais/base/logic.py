import random
from array import array

firmware = array('L', [0]) * 512

GROUND = 6 # 2**6 = 64
HEAPINDEX = lambda s: GROUND - s
SLA = []

def makeSLA():
    for i in range(GROUND):
        makeLine(i)
        # print(f'line\t: {lineGet(i)}' )
        # print(f'u\t: {uGet(i)}')
        # print(f'v\t: {vGet(i)}')
        
    print(SLA)
    
def lineGet(space):
    global SLA
    aux = 2**(space+1) - 2
    beg = aux
    end = 2**(space+1) + aux
    return SLA[beg:end]
    
def uGet(space):
    global SLA
    aux = 2**(space+1) - 2
    beg = aux
    end = 2**(space) + aux
    return SLA[beg:end]

def vGet(space):
    global SLA
    aux = 2**(space+1) - 2
    beg = 2**(space) + aux
    end = 2**(space+1) + aux
    return SLA[beg:end]

def makeLine(space):
    global SLA
    
    size = (space+1)
    line = array('L', [0]) * (2**(size-1)) + array('L', [0]) * (2**(size-1))
    SLA += line

def AL1Bit(space, op):
    u = uGet(space)
    v = vGet(space)
    
    if   op == [0, 0]:
        fn = lambda x, y: x and y
    elif op == [0, 1]:
        fn = lambda x, y: x or y
    elif op == [1, 0]:
        fn = lambda x, y: (not(x) and y) or (x and not(y))
    else:
        fn = lambda x, _: not(x)
        
    result = []
    
    for i in range(len(u)):
        if fn(op(u[i] == 1, v[i] == 1)):
            result.append(1)
        else:
            result.append(0)
    
    return result    

def lineSet(space, value):
    global SLA
    for i,bit in enumerate(value):
        lineGet(space)[i] = bit
        
def uSet(space, value):
    global SLA
    aux = 2**(space+1) - 2
    beg = aux
    
    for i,bit in enumerate(value):
        SLA[i+beg] = bit
        
def vSet(space, value):
    global SLA
    aux = 2**(space+1) - 2
    beg = 2**(space) + aux
    for i,bit in enumerate(value):
        SLA[i+beg] = bit

# Next-Adress(>> 23) | Jam(>>20) | ULA(>>12) | C(>>6) | Mem(>>3) | Bus

MPC = 0
MIR = 0

MAR = 0 # Memory Adress Resgister 
MDR = 0 # Memory Data Register
PC  = 0 
MBR = 0 # Memory byte Register
X = 0
Y = 0
H = 0

N = 0
Z = 1

# BUS = Barramentos ~ "Onde ler, onde Escrever"
BUS_A = 0 
BUS_B = 0 
BUS_C = 0 

AUX = 0xFF_FF_FF_FF # ...1111

M_const = 0x033_33_33_33 # ...0011
N_const = 0x055_55_55_55 # ...0101


# Word Merge
def ParallelMult(A, B, debug = True):
    global M_const, N_const
    
    HalfA = A & M_const
    HalfB = B & M_const
    
    N_debug = N_const & 0b1111
    
    if debug:
        print(f'            A ={A:4b} | HA = {HalfA:4b}')
        print(f'            B ={B:4b} | HB = {HalfB:4b}')
    
    r0 = HalfA &  N_const
    r1 = (HalfA & (N_const << 1)) >> 1
    if debug:
        print(f'           r0 =  {HalfA:2b} & { N_debug:4b}')
        print(f'           r1 = ({HalfA:2b} & {(N_debug << 1):4b}) >> 1')
        print(f'                r1 r0 = {r1:2b}{r0:2b}')
    
    s0 = HalfB &  N_const
    s1 = (HalfB & (N_const << 1)) >> 1
    if debug:
        print(f'           s0 =  {HalfB:2b} & {N_debug:4b}')
        print(f'           s1 = ({HalfB:2b} & {(N_debug << 1):4b}) >> 1')
        print(f'                s1 s0 = {s1:2b}{s0:2b}')
    
    
    sum  =  r0 & s0
    if debug:
        print(f'        r0.s0        = {sum:4b} | Parcial: {sum} ')
    
    sum += (r1 & s0) << 1
    if debug:
        print(f'        (r1.s0) << 1 = {sum:4b} | Parcial: {sum} ')
    
    sum += (r0 & s1) << 1
    if debug:
        print(f'        (r0.s1) << 1 = {sum:4b} | Parcial: {sum} ')
    
    sum += (r1 & s1) << 2
    if debug:
        print(f'        (r1.s1) << 2 = {sum:4b} | Parcial: {sum} ')

    if debug:
        print(f'    Result   {A}*{B} = {sum}')
    
    return sum
    
def Mult4bit(a,b, debug = True):
    global M_const, N_const
    # a = u1 u0
    # b = v1 v0
    
    A = a
    B = b
    
    Prod_u0_v0 = ParallelMult(A,B, False)
    
    sum = Prod_u0_v0
    if debug:
        print(f'    sum : {sum:8b} : {sum}')
    
    A = a >> 2
    B = b
    
    Prod_u1_v0 = ParallelMult(A, B, False) << 2
    
    sum += Prod_u1_v0
    if debug:
        print(f'    sum : {sum:8b} : {sum}')
    
    A = a
    B = b >> 2
    
    Prod_u0_v1 = ParallelMult(A, B, False) << 2
    
    sum += Prod_u0_v1
    if debug:
        print(f'    sum : {sum:8b} : {sum}')
    
    A = a >> 2
    B = b >> 2
    
    Prod_u1_v1 = ParallelMult(A, B, False) << 4
    
    sum += Prod_u1_v1
    if debug:
        print(f'Total : {sum:8b} : {sum}')
    
    return sum
    
def fractalMult(u, v, debug=True, d=3): # 8bits min
    ident = ""
    for _ in range(3 - d):
        ident += '\t' 
        
    dim = 2**(d-1) # 2**(3-1) = 4
    sum = 0

    LowHalf  = 0x0F_0F_0F_0F
    HighHalf = 0xF0_F0_F0_F0
    
    debug_LowHalf = LowHalf & 0xFF
    debug_HighHalf = HighHalf & 0xFF

    def format1(p, p1, p0, c):            
        print(f'{ident}({p :4d}) {c}   : {p :8b}')
        print(f'{ident}\t   & {debug_LowHalf:08b}')
        print(f'{ident}({p0:4d}) {c}0  : {p0 :8b}\n')
        
        print(f'{ident}({p:4d}) {c}   : {p :8b}')
        print(f'{ident}\t   & {debug_HighHalf:08b}')
        print(f'{ident}({p1:4d}) {c}1  : {p1 :8b}\n\n')
    
    u0 = u & LowHalf
    u1 = u & HighHalf
    if debug:
        format1(u, u1, u0, "u")
    u1 = u1 >> dim
    
    v0 = v & LowHalf
    v1 = v & HighHalf
    if debug:
        format1(v, v1, v0, "v")
    v1 = v1 >> dim
    
    if debug:
        print(f'{ident}u = {u:8b}   = {hex(u)}')
        print(f'{ident}u = {u1:4b}, {u0:4b} = {hex(u1)}, {hex(u0)}')
        
        print(f'{ident}v = {v:8b}   = {v}')
        print(f'{ident}v = {v1:4b}, {v0:4b} = {hex(v1)}, {hex(v0)}\n')
    
    print(f'{ident}{u} * {v} << {dim}------------------------')
    if (d < 3): 
        
        Aux0 = Mult4bit(u0, v0, False)
        sum += Aux0
        if debug:
            print(f'{ident}u0*v0 : {Aux0:9b} | Aux0 : {Aux0}')
            print(f'{ident}sum   : {sum :9b} | sum  : {sum}')
        
        Aux1 = Mult4bit(u1, v0, False) << dim
        sum += Aux1
        if debug:
            print(f'{ident}u1*v0 : {Aux1:9b} | Aux1 : {Aux1}')
            print(f'{ident}sum   : {sum :9b} | sum  : {sum}')
        
        Aux0 = Mult4bit(v1, u0, False) << dim
        sum += Aux0
        if debug:
            print(f'{ident}u0*v1 : {Aux0:9b} | Aux0 : {Aux0}')
            print(f'{ident}sum   : {sum :9b} | sum  : {sum}')
        
        Aux1 = Mult4bit(u1, v1, False) << (2*dim)
        sum += Aux1
        if debug:
            print(f'{ident}u1*v1 : {Aux1:9b} | Aux1 : {Aux1}')
            print(f'{ident}->Sum = {sum :9b} = {sum}\n')
    else:        
        Aux0 = fractalMult(u0, v0, False, d-1)
        sum += Aux0
        
        Aux0 = u1
        Aux1 = fractalMult(Aux0, v0, False, d-1) << dim
        sum += Aux1
        
        Aux0 = v1
        Aux0 = fractalMult(Aux0, u0, False, d-1) << dim
        sum += Aux0
        
        Aux0 = u1
        Aux1 = v1
        Aux1 = fractalMult(Aux0, Aux1, False, d-1) << (2*dim)
        sum += Aux1

    print(f'{ident}{u} * {v} = {sum}---------------------\n')
    return sum

def test8bitMult(attemps):
    count_fail = 0
    diffs = []
    msg = ""
    ok = "ok"
    fail = "fail"
    for _ in range(attemps):
        max = 2**8-1
        min = 0
        
        a = random.randint(min, max)
        # max = max - a
        b = random.randint(min, max)
        
        py_res = a*b
        my_res = fractalMult(a, b, False, 3)
        err = (py_res - my_res)/2
        
        if err != 0:
            diffs.append(err)
            count_fail += 1 
            msg = fail
        else:
            msg = ok
        
        print(f'test---{a} * {b}------')
        print(f'Py --> a*b = {py_res}')
        print(f'My --> a*b = {my_res}')
        print(f'err--> {err}')
        print(f'-------{msg}------')

    print(dict(
        count_fail=count_fail,
        diffs=diffs
    ))
        
        
        
        
def wordMult(wordA, wordB):
    sum = 0
    byte = 0xFF 
    u0 = wordA & byte
    v0 = wordA & byte
    
    byte = byte << 8
    u1 = wordA & byte >> 8
    v1 = wordA & byte >> 8
    
    byte = byte << 8
    u2 = wordA & byte >> 2*8
    v2 = wordA & byte >> 2*8
    
    byte = byte << 8
    u3 = wordA & byte >> 3*8
    v3 = wordA & byte >> 3*8
    
    sum += fractalMult(u0, v0, False) 
    sum += fractalMult(u0, v1, False) 
    sum += fractalMult(u0, v2, False) << 1*8
    sum += fractalMult(u0, v3, False) << 2*8
    
    sum += fractalMult(u1, v0, False)
    sum += fractalMult(u1, v1, False) << 1
    sum += fractalMult(u1, v2, False) << 1*8
    
    sum += fractalMult(u2, v0, False)
    sum += fractalMult(u2, v1, False)
    
    sum += fractalMult(u3, v0, False)
    
    return sum
    

# def factralMult(u, v, dim, const = 0x11_11):
#     dimension_const = const
#     debug = dimension_const & 0xFF
    
#     print(f'dim : {dim}')
#     print(f'    const : {hex(dimension_const)}')
#     print(f'    format: {debug:8b} - {debug}')
    
#     dim = dim - 1
#     if ((dim - 1) != 0):
#         next_const = const + 0x22_22
#         factralMult(u, v, dim, next_const)
    
    

def alu(control_bits):
    global BUS_A, BUS_B, BUS_C, N, Z
    
    a = BUS_A 
    b = BUS_B
    out = 0
    
    shift_bits = control_bits & 0b11000000
    shift_bits = shift_bits >> 6
    
    control_bits = control_bits & 0b00111111
    # F0 F1 Enb_A Enb_B Invert_A Increment_C 
    # F0| F1 
    # 0 | 0 -> A & B
    # 0 | 1 -> A | B
    # 1 | 0 ->   ~ B
    # 1 | 1 -> A + B
    
    # Python:
    #   p | q -> OR bit a bit 
    #   p & q -> AAND bit a bit
    #   p ^ q -> XOR bit a bit 
    #     ~ p -> NEG bit a bit ( Complemento )

    operation = (control_bits & 0b11_00_0_0) >> 4 
    F0 = operation & 0b10
    F1 = operation & 0b01
    
    enable = (control_bits & 0b00_11_0_0) >> 2
    enbA = enable & 0b10
    enbB = enable & 0b01
    
    InvertA = (control_bits & 0b00_00_1_0) >> 1
    
    Increment_C = (control_bits & 0b00_00_0_1)
    
    newA = enbA*a 
    if InvertA == 1:
        newA = ~newA
    
    newB = enbB*b    
     
    if operation == 0b00:
        out = newA & newB
    elif operation == 0b01: 
        out = newA | newB
    elif operation == 0b10:
        out = newA ^ newB   # if newA = 0 -> Xor(0, newB) = ~newB
    elif operation == 0b11: 
        out = newA + newB
    else:
        print("Unexpected Condition for ALU - OPCODE")
    
    if Increment_C == 1:
        out = out + AUX
        
    if out == 0:
        N = 0
        Z = 1
    else:
        N = 1
        Z = 0
        
    if shift_bits == 0b01:
        out = out << 1
    elif shift_bits == 0b10:
        out = out >> 1
    elif shift_bits == 0b11:
        out = out << 8 
        
    BUS_C = out
    
