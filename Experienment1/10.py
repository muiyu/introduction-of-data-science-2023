def compute(value, local, x):
    point = 1.0
    for i in range(local+1): 
        point = point/10
        i = i
    for i in range(11):
        if (x+i*point)**3 == value:
            return x+i*point
        if (x+i*point)**3 > value:
            return x+(i-1)*point
    
i = input()
i = float(i)
x = 0
if_int = False
while x**3 < i:
    x += 1
    if x**3 == i:
        print(x)
        if_int = True
        break
    if x**3 > i:
        x = x-1
        break


if if_int == False:
    for local in range(6):
        x = compute(i, local, x)
    print(x)
else:
    pass
    