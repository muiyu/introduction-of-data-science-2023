import numpy as np
import time

def measure_sorting_time(arr, sorting_kind):
    start_time = time.time()
    sorted_arr = np.sort(arr, kind=sorting_kind)
    end_time = time.time()
    return end_time - start_time

array_lengths = [1000000, 10000000, 100000000]
sorting_algorithms = ['quicksort', 'heapsort', 'mergesort']

for length in array_lengths:
    print(f"对长度为 {length} 的递增数组进行排序:")
    arr = np.arange(1, length+1) 

    for sorting_algorithm in sorting_algorithms:
        execution_time = measure_sorting_time(arr, sorting_algorithm)
        print(f"{sorting_algorithm} 执行时间: {execution_time} 秒")

    print()
