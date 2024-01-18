char = input()
if_same = False

char = [i for i in char]

for i in range(len(char)-1):
    if char[i] == char[i+1]:
        print("Have at least 2 proxiamte same characters")
        if_same = True
        break
if if_same == False:
    print("No proxiamte same characters")