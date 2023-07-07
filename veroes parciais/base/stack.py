from array import array

stack = []
Arch  = 6 # 64

# INSTRUCTION GLOBAL VARIABLES
# V1
BUS_A = 0 
BUS_B = 0 
TRANSFORM_0 = 0b11 # DEFAULT == NOT
TRANSFORM_1 = 0b11 # DEFAULT == NOT

#V2 
firmware = [
                array('B', [0]) * (2**32)
            ] * 512 
#                ) * 16 Debug 
# ---- ---- ---- ---- ---- ---- ---- ----

heapMag   = Arch # letter = 2 bits, word = 2 letters, operation = 2 words
heapLen    = (2**heapMag - 1)
left    = lambda i: (2 * i + 1) & (heapLen)
right   = lambda i: (2 * i + 2) & (heapLen)
#     0     - 0
#    / \
#   1   2   - 1
#  / \ / \
# 3  4 5  6 - 2
# ...   ... - 5
Heap = array('B', [0b00]) * (heapLen)



def readTier(tier):
    global Heap
    tier = tier & ((heapMag << 2) - 1)
    beg = 2**tier
    end = 2*beg
    
    beg = beg - 1
    end = end - 1 
    
    return Heap[beg:end]
    
def writeTier(tier, input):
    global Heap
    
    tier = tier & ((heapMag << 2) - 1)
    beg = 2**tier
    end = 2*beg
    
    beg = beg - 1
    end = end - 1 
    
    for i, letter in enumerate(input):
        rel_i = i + beg
        Heap[rel_i] = letter
    
    return Heap[beg:end]
    
def readRegister(tier, reg):
    global Heap
    
    tier = tier & ((heapMag << 2) - 1)
    reg = reg & 0b1
    
    beg = 2**tier
    end = 2*beg
    
    beg = beg - 1
    end = end - 1 
    mid = (beg + end) >> 1

    if reg == 0: 
        # read u
        return Heap[beg:mid]
    else:
        # read v
        return Heap[mid:end]

def toArr(value):
    binStr = bin(value)[::-1]
    size = 2
    
    while (value >> size) > 0:
        size = 2*size
        
    arr = array('B', [0]) * (size//2)
    for i, bit in enumerate(binStr):
        if bit == "1":
            if i % 2 == 0:
                arr[i//2] += 0b1
            else:
                arr[i//2] += 0b10
    
    # fmtArr = [f'{dup:02b}' for dup in arr]
    # print(fmtArr, sep=" ")
    # print(binStr)
    
    return arr

def toNum(arr):
    num = 0
    for i,dup in enumerate(arr):
        num += (dup << (2*i))
        print(f'num = {num:08b}')
        
    return num