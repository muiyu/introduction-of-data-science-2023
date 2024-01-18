def square_root(c):
    i = 0
    g = 0
    for j in range(0, c+1):
        if(j ** 2 > c and g == 0):
            g = j - 1
    while(abs(g ** 2 - c) > 0.00001):
        g += 0.000001
        i += 1
        print(f"{i} times")
        print(f"g = {g}")

square_root(2)