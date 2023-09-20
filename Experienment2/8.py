def calculate_pi_leibniz(iterations):
    pi_estimate = 0
    for i in range(iterations):
        pi_estimate += (-1) ** i / (2 * i + 1)
    return 4 * pi_estimate

pi_approximation = calculate_pi_leibniz(10000000)
print("{:.10f}".format(pi_approximation))


import random
def calculate_pi_monte_carlo(num_samples):
    inside_circle = 0
    for _ in range(num_samples):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        distance = x ** 2 + y ** 2
        if distance <= 1:
            inside_circle += 1
    return 4 * (inside_circle / num_samples)

pi_approximation = calculate_pi_monte_carlo(100000000)
print("{:.10f}".format(pi_approximation))


import math
def calculate_pi_archimedes(iterations):
    num_sides = 6
    pi_approximation = 0
    for _ in range(iterations):
        rad = 360.0 / num_sides
        rad = math.radians(rad)
        pi_approximation = num_sides * math.sqrt(1 - math.cos(rad)) / math.sqrt(2)
        num_sides *= 2
    return pi_approximation

pi_approximation = calculate_pi_archimedes(12)
print("{:.10f}".format(pi_approximation))