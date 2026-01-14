from textwrap import dedent

from agentica_internal.repl.repl import *


def verify_traceback_avoids_repl():
    repl = BaseRepl()
    ev = repl.run_code('''
    def foo():
        1/0
    foo()
    ''')

    expected = '''
    Traceback (most recent call last):
      <repl> line 4
        foo()
      <repl> line 3, in foo
        1/0
    ZeroDivisionError: division by zero
    '''
    assert ev.error
    assert ev.error.traceback == dedent(expected).lstrip()


def verify_traceback_avoids_agentica():
    def internal_fn():
        for i in range(5):
            print(i / (3 - i))

    repl = BaseRepl()
    repl.set_global('internal_fn', internal_fn)
    ev = repl.run_code('''internal_fn()''')

    expected = '''
    Traceback (most recent call last):
      <repl> line 1
        internal_fn()
    ZeroDivisionError: division by zero
    '''
    assert ev.error
    assert ev.error.traceback == dedent(expected).lstrip()


def verify_traceback_includes_other():
    repl = BaseRepl()
    ev = repl.run_code('''
    import collections
    collections.Counter(999)
    ''')

    expected = '''
    Traceback (most recent call last):
      <repl> line 3
        collections.Counter(999)
      File "/python3
        self.update(iterable, **kwds)
      File "/python3
        _count_elements(self, iterable)
    TypeError: 'int' object is not iterable
    '''
    actual = censor_tb(ev.error.traceback)
    expected = dedent(expected).strip()
    assert actual == expected


def censor_tb(expected: str):
    return '\n'.join(
        PREFIX if line.startswith('  File "/python3') else line for line in expected.splitlines()
    )


PREFIX = '  File "/python3'

if __name__ == '__main__':
    verify_traceback_avoids_repl()
    verify_traceback_avoids_agentica()
    verify_traceback_includes_other()
