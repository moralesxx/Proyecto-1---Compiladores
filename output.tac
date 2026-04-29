# === TAC Generado ===
# array nums[5]
nums[0] = 3
nums[1] = 1
nums[2] = 4
nums[3] = 1
nums[4] = 5
total = 0
i = 0
L1:
if i < 5 goto L2
goto L3
L2:
t1 = nums[i]
t2 = t1 % 2
r = t2
if r == 0 goto L4
goto L5
L4:
t3 = nums[i]
t4 = total + t3
total = t4
L5:
t5 = i + 1
i = t5
if total > 10 goto L6
goto L7
L6:
goto L3
L7:
goto L1
L3:
suma = 0
i = 0
L8:
if i < 5 goto L9
goto L11
L9:
t6 = nums[i]
if t6 == 1 goto L12
goto L13
L12:
goto L10
L13:
t7 = nums[i]
t8 = suma + t7
suma = t8
L10:
t9 = i + 1
i = t9
goto L8
L11:
begin_func fibonacci
param n
if n <= 1 goto L14
goto L15
L14:
return n
L15:
t10 = n - 1
arg t10
t11 = call fibonacci, 1
t12 = n - 2
arg t12
t13 = call fibonacci, 1
t14 = t11 + t13
return t14
end_func fibonacci
begin_func maximo
param a
param b
if a > b goto L16
goto L17
L16:
return a
L17:
return b
end_func maximo
msg = "Fibonacci(7) = "
print msg
arg 7
t15 = call fibonacci, 1
print t15
print "Total pares del arreglo: "
print total
print "Suma sin unos: "
print suma
print "Maximo entre 42 y 17: "
arg 42
arg 17
t16 = call maximo, 2
print t16