import agentica_internal.testing.examples.modules.mixin.a as a
import agentica_internal.testing.examples.modules.mixin.b as b
import agentica_internal.testing.examples.modules.mixin.c as c
import agentica_internal.testing.examples.modules.mixin.post as post


def verify_mixin():
    """basic mixin: child module overrides are called by inherited functions"""
    print(f'{a.x=}')
    print(f'{a.foo()=}')
    print(f'{a.bar()=}')
    print(f'{b.foo()=}')
    print(f'{b.bar()=}')
    print(f'{b.x=}')
    assert a.x == 3 * 10
    assert a.foo() == 'a.foo'
    assert a.bar() == ('a.bar', 'a.foo')
    assert b.foo() == 'b.foo'
    assert b.bar() == ('a.bar', 'b.foo')
    assert b.x == 2 * 10


def verify_closure_rewriting():
    """mixin rewrites functions captured in decorator closures"""
    # b.decorated_caller should use b.helper and b.foo
    print(f'{b.decorated_caller()=}')
    assert b.decorated_caller() == ['b.helper', 'b.foo']

    # c.decorated_caller should use c.helper and c.foo (both overridden)
    print(f'{c.decorated_caller()=}')
    assert c.decorated_caller() == ['c.helper', 'c.foo']

    # basic mixin still works for c
    print(f'{c.foo()=}')
    print(f'{c.bar()=}')
    assert c.foo() == 'c.foo'
    assert c.bar() == ('a.bar', 'c.foo')


def verify_init_module_globals():
    """
    init_module hook writes to child module's globals, not parent's.

    Pattern:
    1. Parent defines a module-level dict (_REGISTRY)
    2. @init_module hook populates it by scanning for is_*/has_* functions
    3. A function (get_registry) returns this dict
    4. Child modules should see their own functions in the dict
    """
    # a should only have is_feature_a
    a_reg = a.get_registry()
    print(f'{a_reg=}')
    assert 'is_feature_a' in a_reg
    assert 'is_feature_b' not in a_reg
    assert 'is_feature_c' not in a_reg

    # b should have is_feature_a (inherited) AND is_feature_b (its own)
    b_reg = b.get_registry()
    print(f'{b_reg=}')
    assert 'is_feature_a' in b_reg
    assert 'is_feature_b' in b_reg
    assert 'is_feature_c' not in b_reg

    # c should have all three
    c_reg = c.get_registry()
    print(f'{c_reg=}')
    assert 'is_feature_a' in c_reg
    assert 'is_feature_b' in c_reg
    assert 'is_feature_c' in c_reg


def verify_finalize():
    """finalize runs code after module is loaded"""
    print(f'{post.x=}')
    assert post.x == 20
    print(f'{post.y=}')
    assert post.y == 30


if __name__ == '__main__':
    verify_mixin()
    verify_closure_rewriting()
    verify_init_module_globals()
    verify_finalize()
    print('All mixin tests passed!')
