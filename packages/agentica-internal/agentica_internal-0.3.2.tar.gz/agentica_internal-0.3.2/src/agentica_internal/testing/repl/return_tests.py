from agentica_internal.repl.repl import *


def verify_return_statement():
    repl = BaseRepl()
    ev = repl.run_code('''
    return 1 + 1
    ''')
    assert not ev.error
    assert ev.return_value == 2


def verify_return_statement_nesting():
    repl = BaseRepl()
    # a return in a function should not cause a global return
    ev = repl.run_code('''
    def foo():
        return 1 + 1
    for i in range(5,10):
        return foo() + i
    ''')
    assert not ev.error
    assert ev.return_value == 7


def verify_return_variable():
    repl = BaseRepl()
    repl.options.return_var = 'result'
    ev = repl.run_code('''
    result = 9
    ''')
    assert not ev.error
    assert ev.return_value == 9


def verify_return_variable_nesting():
    repl = BaseRepl()
    repl.options.return_var = 'result'
    # setting a local result in a function should not cause a return
    # TODO: recognise 'global result' as an exception to this
    ev = repl.run_code('''
    def foo():
        result = 9
    foo()
    ''')
    assert not ev.error
    assert not ev.has_return_value


def verify_does_not_catch_returnexit():
    repl = BaseRepl()
    ev = repl.run_code('''
    try:
        return 'good'
    except:
        return 'bad'
    ''')
    assert ev.return_value == 'good'

    ev = repl.run_code('''
    try:
        return 'good'
    finally:
        pass
    ''')
    assert ev.return_value == 'good'

    ev = repl.run_code('''
    try:
        return 'good'
    except SystemExit:
        pass
    ''')
    assert ev.return_value == 'good'

    ev = repl.run_code('''
    try:
        try:    
            return 'good'
        except:
            return 'bad'
    except:
        return 'bad'
    ''')
    assert ev.return_value == 'good'


if __name__ == '__main__':
    verify_return_statement()
    verify_return_statement_nesting()
    verify_return_variable()
    verify_return_variable_nesting()
    verify_does_not_catch_returnexit()
