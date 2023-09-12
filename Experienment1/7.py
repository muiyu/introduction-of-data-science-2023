l = input().split()
try:
    L = [int(value) for value in l]
except ValueError:
    print("输入无效。请确保所有输入都是有效的整数。")

for i in range(len(L)):
    print(L[len(L)-i-1], end=" ")