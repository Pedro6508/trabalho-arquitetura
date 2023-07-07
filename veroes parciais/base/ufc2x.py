from array import array

import memory

firmware = array('L', [0]) * 512

# main: PC <- PC + 1; MBR <- read_byte(PC); goto MBR
firmware[0] =   0b000000000_100_00110101_001000_001_001
#####################################################
# HALT
firmware[255] = 0b000000000_000_00000000_000000_000_000
#####################################################
# X = X + memory[address]

## 2: PC <- PC + 1; fetch; goto 3
firmware[2] = 0b000000011_000_00110101_001000_001_001

## 3: MAR <- MBR; read_word(MAR); goto 4
firmware[3] = 0b000000100_000_00010100_100000_010_010

## 4: H <- MDR; goto 5
firmware[4] = 0b000000101_000_00010100_000001_000_000

## 5: X <- H + X; goto 0
firmware[5] = 0b000000000_000_00111100_000100_000_011
#####################################################
# X = X - memory[address]

## 6: PC <- PC + 1; fetch; goto 7
firmware[6] = 0b000000111_000_00110101_001000_001_001

## 7: MAR <- MBR; read; goto 8
firmware[7] = 0b000001000_000_00010100_100000_010_010

## 8: H <- MDR; goto 9
firmware[8] = 0b000001001_000_00010100_000001_000_000

## 9: X <- X - H; goto 0
firmware[9] = 0b000000000_000_00111111_000100_000_011
#####################################################
# memory[address] = X

## 10: PC <- PC + 1; fetch; goto 11
firmware[10] = 0b00001011_000_00110101_001000_001_001

## 11: MAR <- MBR; goto 12
firmware[11] = 0b00001100_000_00010100_100000_000_010

## 12: MDR <- X; write; goto 0
firmware[12] = 0b00000000_000_00010100_010000_100_011
#####################################################
# goto address 

## 13: PC <- PC + 1; fetch; goto 14
firmware[13] = 0b00001110_000_00110101_001000_001_001

## 14: PC <- MBR; fetch; goto MBR
firmware[14] = 0b00000000_100_00010100_001000_001_010

# if X == 0 goto address

## 15: X <- X; if alu = 0 goto 272 else goto 16
firmware[15] = 0b00010000_001_00010100_000100_000_011

## 16: PC <- PC + 1; goto 0
firmware[16] = 0b00000000_000_00110101_001000_000_001

## 272: goto 13
firmware[272]= 0b00001101_000_00000000_000000_000_000
#####################################################
# mult X Y 

# H <- B
firmware[17] = (
    (bin(17+1)      >> 23) + # Next-Adress( goto 18 )
    (0b000          >> 20) + # Jam( no jump )
    (0b00_01_01_00  >> 12) # ULA( AvB enbB -> B ) ~ enbA = 0 => A = 0
)            

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

# auxiliares
AUX = 1 # auxiliar padrão
auxList = [
    2**32,
    2**16,
    2**8,
    2**4,
    2**2
]

AuxMult32 = 0xAA_AA_AA_AA

def make_firmware_sum():
    # sum ULA : 0b00111100
    # SLL8*0 SRA1*0 F0 F1 enbA enbB InvA*0 IncC*0
    WRegs = (MIR & 0b00000000000000000000111111000000) >> 6
    # p <- H + q
    
def read_regs(reg_num):
    global MDR, PC, MBR, X, Y, H, BUS_A, BUS_B
    
    BUS_A = H
    
    if reg_num < 4:
        if reg_num == 0:
            BUS_B = MDR
        elif reg_num == 1:
            BUS_B = PC
        elif reg_num == 2:
            BUS_B = MBR
        elif reg_num == 3:
            BUS_B = X
    else:
        BUS_A = X
        BUS_B = Y
        
        if reg_num == 4: 
            H = MDR
        elif reg_num == 5:
            H = PC
        elif reg_num == 6:
            H = MBR
        else: 
            H = AuxMult32 
            
def write_regs(reg_bits):
    global MAR, BUS_C, MDR, PC, X, Y, H

    if reg_bits & 0b100000:
        MAR = BUS_C
        
    if reg_bits & 0b010000:
        MDR = BUS_C 
        
    if reg_bits & 0b001000:
        PC = BUS_C
        
    if reg_bits & 0b000100:
        X = BUS_C
        
    if reg_bits & 0b000010:
        Y = BUS_C
        
    if reg_bits & 0b000001:
        H = BUS_C
            
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

def next_instruction(next, jam):

    global MPC, MBR, N, Z
    
    if jam == 0b000:
        MPC = next
        return
        
    if jam & 0b001:                 # JAMZ
        next = next | (Z << 8)
        
    if jam & 0b010:                 # JAMN
        next = next | (N << 8)

    if jam & 0b100:                 # JMPC
        next = next | MBR
        
    MPC = next


def memory_io(mem_bits):

    global PC, MBR, MDR, MAR
    
    if mem_bits & 0b001:                # FETCH
       MBR = memory.read_byte(PC)
       
    if mem_bits & 0b010:                # READ
       MDR = memory.read_word(MAR)
       
    if mem_bits & 0b100:                # WRITE
       memory.write_word(MAR, MDR)
       
def step():
   
    global MIR, MPC
    
    MIR = firmware[MPC]
    
    if MIR == 0:
        return False    
    
    read_regs        ( MIR & 0b00000000000000000000000000000111)
    alu              ((MIR & 0b00000000000011111111000000000000) >> 12)
    write_regs       ((MIR & 0b00000000000000000000111111000000) >> 6)
    memory_io        ((MIR & 0b00000000000000000000000000111000) >> 3)
    next_instruction ((MIR & 0b11111111100000000000000000000000) >> 23,
                      (MIR & 0b00000000011100000000000000000000) >> 20)
                      
    return True




