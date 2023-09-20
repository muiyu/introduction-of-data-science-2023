def square_root(c):
    g = c/3
    i = 0
    while(abs(g**3 - c)>1e-12):
        g = (2*g+c/(g**2))/3
        i += 1
        print("第%d次迭代的结果为%.32f"%(i,g))

square_root(8)