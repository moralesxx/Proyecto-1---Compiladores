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
begin_func fibonacci
param n
if n <= 1 goto L8
goto L9
L8:
return n
L9:
t6 = n - 1
arg t6
t7 = call fibonacci, 1
t8 = n - 2
arg t8
t9 = call fibonacci, 1
t10 = t7 + t9
return t10
end_func fibonacci
msg = "Fibonacci(7) = "
print msg
arg 7
t11 = call fibonacci, 1
print t11
print "Total pares: "
print total