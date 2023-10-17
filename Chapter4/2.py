###以下代码将基于问题1（判断质数）编写的程序，给出一个统计程序运行时间的示例程序###
import time

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

n = input()
n = int(n)
start = time.time()
is_prime(n)
end = time.time()
print(f"使用了{(end-start):.8f}s")