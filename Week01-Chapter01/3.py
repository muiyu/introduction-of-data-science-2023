A = input()
list = A.split()
try:
    values = [int(value) for value in list]
except ValueError:
    print("输入无效。请确保所有输入都是有效的整数。")
sorted_values = sorted(values)

print(sorted_values[0], sorted_values[1], sorted_values[2])