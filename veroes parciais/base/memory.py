from array import array

# memória de 32 bits
memory = array("L", [0]) * (1024*1024//4)  # 1MB / 262.144 words (218) / 1 word = 4 bytes
# 0 - 262.143

# funções de acesso (ignorar bits de overflow)

def read_word(add):
    add = add & 0b111111111111111111
    return memory[add]

def write_word(add, val):
    add = add & (2**18-1) 
    val = val & 0xFFFFFFFF
    memory[add] = val

def read_byte(add):
    # determinar qual a palavra
    add = add & 0b1111111111111111111 # 2^20-1
    end_word = add >> 2   # divisão por 4
    val_word = memory[end_word]

    # determinar o byte dentro da palavra
    end_byte = add & 0b11   # resto da divisão por 4
    val_byte = val_word >> (end_byte << 3)
    val_byte = val_byte & 0xFF
    return val_byte

def write_byte(add,val):
    val = val & 0xFF                   # e.g. val = DD
    add = add & 0b1111111111111111111  # 2^20-1
    end_word = add >> 2   # divisão por 4
    val_word = memory[end_word]        # 34CC4F33

    end_byte = add & 0b11   # resto da divisão por 4
    
    mask = ~(0xFF << (end_byte << 3))  # FF00FFFF
    val_word = val_word & mask         # 34004F33

    val = val << (end_byte << 3)       # val = 00DD0000
 
    val_word = val_word | val          # val_word = 34DD4F33

    memory[end_word] = val_word