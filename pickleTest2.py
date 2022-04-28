a = None
def f2():
    pass

def print2(*args):
    print(a)
    print(*args)

def print3(*args):
    print(f2(1, 2))
    print(*args)