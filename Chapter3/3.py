import re

def validate_id_card(id_card):
    pattern_30 = r"^([1-5]\d{5}(19|20)\d{2}(04|06|09|11)([0-2]\d|30)\d{3}(\d|X))$"
    pattern_31 = r"^([1-5]\d{5}(19|20)\d{2}(01|03|05|07|08|10|12)([0-2]\d|3[0-1])\d{3}(\d|X))$"
    pattern_28 = r"^([1-5]\d{5}(19|20)\d{2}02[0-2]\d{4}(\d|X))$"
    if re.match(pattern_28, id_card) or re.match(pattern_30, id_card) or re.match(pattern_31, id_card):
        return True
    else:
        return False

# 测试
id_card = input("Please input your id number: ")
if validate_id_card(id_card):
    print("valid")
else:
    print("invalid")
