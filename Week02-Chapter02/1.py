###尝试从小到大分解了几个数字之后，发现了规律，并根据该规律编写了代码

def find_max_list(n, max_list):
    if n == 3:
        max_list.append(3)
    elif n == 2:
        max_list.append(2)
    elif n == 1:
        max_list.append(1)
    elif n == 4:
        max_list.extend([2, 2])
    elif n == 5:
        max_list.extend([3, 2])
    elif n == 6:
        max_list.extend([3, 3])
    else:
        element1 = n // 2
        element2 = n - element1
        find_max_list(element1, max_list)
        find_max_list(element2, max_list)



import sys
sys.setrecursionlimit(1000)

n = input()
n = int(n)
max_list = []
find_max_list(n, max_list)
print(max_list)

###如果n=2001
find_max_list(2001, max_list)
print(max_list)