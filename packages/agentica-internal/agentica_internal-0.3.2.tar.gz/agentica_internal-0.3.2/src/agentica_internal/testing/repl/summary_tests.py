from agentica_internal.repl.repl import *


def verify_run_code_summary():
    repl = BaseRepl()
    summary = repl.run_code_info('2 + 2')
    assert summary.out_str == '4'
    assert not summary.has_error
    assert not summary.has_return_value

    summary = repl.run_code_info('2 + 2')
    assert summary.out_str == '4'
    assert not summary.has_return_value

    summary = repl.run_code_info('1 / 0')
    assert summary.has_uncaught_error
    assert summary.exception_name == 'builtins.ZeroDivisionError'
    assert not summary.has_raised_error

    summary = repl.run_code_info('raise KeyError(2)')
    assert summary.has_raised_error
    assert not summary.has_uncaught_error
    assert summary.exception_name == 'builtins.KeyError'

    summary = repl.run_code_info('import math')
    assert summary.imported == ('math',)

    summary = repl.run_code_info('x = 5')
    assert summary.added_locals == ('x',)

    summary = repl.run_code_info('x = 6')
    assert summary.changed_locals == ('x',)

    summary = repl.run_code_info('del x')
    assert summary.removed_locals == ('x',)


if __name__ == '__main__':
    verify_run_code_summary()
