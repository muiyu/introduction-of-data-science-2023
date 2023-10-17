float_number = float(input())
integer_part = int(float_number)
decimal_part = float_number - integer_part
binary_integer_part = bin(integer_part)[2:]
binary_decimal_part = ""


for _ in range(32):
    decimal_part *= 2
    if decimal_part >= 1:
        binary_decimal_part += "1"
        decimal_part -= 1
    else:
        binary_decimal_part += "0"

binary_string = f"{binary_integer_part}.{binary_decimal_part:.12}"
print(binary_string)