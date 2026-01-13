import assign_overload
import wrapt


class T(wrapt.ObjectProxy):        
    def _assign_(self, value, *annotation):
        print(f"called with {value}")
        self.__wrapped__ = value
        return self


class A:
    a = T(10)


class B:
    __slots__ = ["a"]


class Descriptor1:
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner = None):
        return self.value

    def __set__(self, instance, value):
        self.value = value


class Descriptor2:
    def __get__(self, instance, owner = None):
        print("in Descriptor2.__get__")


class C:
    a = Descriptor1(T(10))


class Meta(type):
    def a(cls):
        print("in 'a' function")

    
class D:
    a = T(10)


class E(D, metaclass = Meta):
    pass

    
def test1():
    global b
    #a, b = T(), T()
    print("here")
    b = c = d = T(10)
    b = 20
    print(b)
    print(type(b))


def test2():
    a = A()
    a.a = T(5)
    a.a = 30
    print(a.a)    
    del a.a
    print(a.a)


def test3():
    b = B()
    b.a = T(10)
    b.a = "abc"
    print(b.a)
    c = C()
    c.a = "def"
    print(c.a)
    

def test4():    
    E.a = 20
    if D.a != 10:
        raise ValueError("Base class member changed value after assigning to derived class")

    
def main():
    test1()
    print()
    test2()
    print()
    test3()
    print()
    test4()


if assign_overload.patch_and_reload_module():
    main()
