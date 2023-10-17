import numpy as np

a = np.random.randint(1, 10, size=10).tolist()
b = []

for i in range(0, len(a)):
    number = 1
    for j in range(1, i):
        number *= a[j]
    for j in range(i + 1, len(a)):
        number *= a[j]
    b.append(number)

print(a)
print(b)