from agentica_internal.cpython.shed.load import get_shed_function, get_shed_method, get_shed_module


def verify_builtins_shed():
    module = get_shed_module('builtins')
    assert 'str' in getattr(module, '__all__', ())
    method = get_shed_method(str, 'capitalize')
    assert method.__qualname__ == 'str.capitalize'
    assert method.__module__ == 'builtins'
    assert method.__annotations__.get('return') == str


def verify_math_shed():
    module = get_shed_module('math')
    assert 'sqrt' in getattr(module, '__all__', ())
    fn = get_shed_function('math', 'sqrt')
    assert fn.__module__ == 'math'
    assert fn.__name__ == 'sqrt'
    assert fn.__annotations__.get('return') == float


def verify_not_in_shed():
    class MyClass: ...

    MyClass.__module__ = 'my_module'
    method = get_shed_method(MyClass, 'foo')
    assert method.__module__ == 'my_module'
    assert method.__name__ == 'foo'
    assert method.__qualname__ == 'MyClass.foo'
    assert not method.__annotations__

    method = get_shed_function('my_module', 'foo')
    assert method.__module__ == 'my_module'
    assert method.__name__ == 'foo'
    assert method.__qualname__ == 'foo'
    assert not method.__annotations__


if __name__ == '__main__':
    verify_builtins_shed()
    verify_math_shed()
    verify_not_in_shed()
