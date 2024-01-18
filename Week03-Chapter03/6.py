x = input()
x = int(x)

if x < 0 :
    print("Invalid input!")
    exit(0)
elif x >= 0 and x < 60 :
    print("F")
elif x >= 60 and x < 75 :
    print("P")
elif x >= 75 and x < 90 :
    print("G")
elif x >= 90 and x <= 100 :
    print("E")