from agentica_internal.repl.repl import *


def verify_explicit_raise():
    repl = BaseRepl()
    error = repl.run_code("raise KeyError(1)").error
    assert error
    assert error.raised
    assert isinstance(error.exception, KeyError)


def verify_ignores_reraise():
    repl = BaseRepl()
    error = repl.run_code('''
    try:
        1/0
    except:
        raise
    ''').error
    assert error
    assert not error.raised
    assert isinstance(error.exception, ZeroDivisionError)


if __name__ == '__main__':
    verify_explicit_raise()
    verify_ignores_reraise()
