.code
x = 50
t1 = x > 10
if t1 goto L1
goto L2
L1:
goto L3
L2:
L3:
y = 5
L4:
t2 = y > 0
if t2 goto L5
goto L6
L5:
t3 = y - 1
y = t3
goto L4
L6: