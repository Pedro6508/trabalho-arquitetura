 goto main
 wb 0
 
r ww 0 
a ww 77
b ww 9
c ww 0
d ww 0
u ww 1
m ww 0
z ww 0 

main goto copia
ret2 goto maior
ret  add x, m
     jz x, troca
     sub x, m

mult add x, b             # if b=0 goto final
     jz x, final
     sub x, b
     
     add x, a             # r = r + a
     add x, r
     mov x, r
     sub x, r
     
     add x, b             # b = b - 1
     sub x, u     
     mov x, b
     sub x, b
     
     goto mult
     
maior add x, c
      jz x, final_maior   # if x=0 goto final 
      
      sub x, u            # a = a - 1
      mov x, c
      sub x, c
      
      add x, d      
      jz x, final2_maior  # if x=0 goto final2
      
      sub x, u            # b = b - 1
      mov x, d
      sub x, d
      
      goto maior
      
final2_maior add x, u     # m = 1
             mov x, m
             sub x, m
      
final_maior goto ret
     
troca  add x, a   # z = a
       mov x, z
       sub x, z

       add x, b   # a = b
       mov x, a
       sub x, a
          
       add x, z   # b = z
       mov x, b
       sub x, b

       goto mult
       
copia  add x, a   # c = a
       mov x, c
       sub x, a

       add x, b   # d = b
       mov x, d
       sub x, b

       goto ret2
 
final halt
     
     
     
