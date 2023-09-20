import time

start_time = time.perf_counter()
a = 2 ** 10
print(a)
end_time = time.perf_counter()
print(f"{end_time-start_time}")

start_time = time.perf_counter()
b = 2 ** 20
print(b)
end_time = time.perf_counter()
print(f"{end_time-start_time}")

start_time = time.perf_counter()
c = 2 ** 30
print(c)
end_time = time.perf_counter()
print(f"{end_time-start_time}")

start_time = time.perf_counter()
d = 2 ** 40
print(d)
end_time = time.perf_counter()
print(f"{end_time-start_time}")

start_time = time.perf_counter()
e = 2 ** 50
print(e)
end_time = time.perf_counter()
print(f"{end_time-start_time}")
