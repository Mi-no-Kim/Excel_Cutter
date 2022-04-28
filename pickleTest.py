import pickleTest2

def add(a, b):
    return a+b

pickleTest2.a = 1
pickleTest2.print2("!!!")

pickleTest2.f2 = add
pickleTest2.print3("???")