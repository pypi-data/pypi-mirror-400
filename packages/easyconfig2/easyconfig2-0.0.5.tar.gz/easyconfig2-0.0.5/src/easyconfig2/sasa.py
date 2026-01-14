class Dummy:
    pass


class A:
    def __init__(self):
        self.e1 = 1
        self.e2 = 2


a = A()
o1 = Dummy()
setattr(a, "e3", o1)
setattr(o1, "e4", 4)

print(a.e3.e4)
