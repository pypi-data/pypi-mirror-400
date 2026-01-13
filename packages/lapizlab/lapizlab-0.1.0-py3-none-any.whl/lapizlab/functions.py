from sys import setrecursionlimit

setrecursionlimit(2000)

def factorial(a):
    if a == 1:
        return 1
    else:
        return a * factorial(a-1)
    