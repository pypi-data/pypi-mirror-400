from agentica_internal.warpc.magic_utils import create_magic_proxy_function


class MyClass: ...


abc = ('a', 'b', 'c')
obj = object()


def original_function(a: int, b: str = 'b', c: tuple = abc, d=obj) -> dict[str, object]:
    """docstring"""
    return {'a': a, 'b': b, 'c': c, 'd': d}


def forward_to_original_function(*args, **kwargs):
    return original_function(*args, **kwargs)


def test_magic_proxy_function():
    proxy_function = create_magic_proxy_function(original_function, forward_to_original_function)
    assert proxy_function.__annotations__ == original_function.__annotations__
    assert proxy_function.__module__ == original_function.__module__
    assert proxy_function.__doc__ == original_function.__doc__
    assert proxy_function.__name__ == original_function.__name__
    assert proxy_function.__qualname__ == original_function.__qualname__
    assert proxy_function(0) == original_function(0)
    assert proxy_function(1, 'x') == original_function(1, 'x')
    assert proxy_function(2, 'y', ()) == original_function(2, 'y', ())
    assert proxy_function(3, 'z', ('a',), True) == original_function(3, 'z', ('a',), True)
