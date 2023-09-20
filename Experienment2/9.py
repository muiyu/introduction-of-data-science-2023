import random as rd
import math

n = 1000000
#partition 1
num_under_curve = 0
for i in range(n):
    x = rd.uniform(2, 3)
    y = rd.uniform(0, 9)
    if y <= x ** 2:
        num_under_curve += 1

area_1 = num_under_curve / n * 9
#partition 2
num_under_curve = 0
for i in range(n):
    x = rd.uniform(2, 3)
    y = rd.uniform(0, 3)
    if y <= x * math.sin(x):
        num_under_curve += 1

area_2 = 4 * (num_under_curve / n) * 3

print("%.10f" %(area_1+area_2))