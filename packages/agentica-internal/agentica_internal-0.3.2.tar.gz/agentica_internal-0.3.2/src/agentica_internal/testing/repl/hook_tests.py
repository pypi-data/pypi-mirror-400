from typing import Any

from agentica_internal.repl.repl import *


def verify_print_hook():
    class MaklovichRepl(BaseRepl):
        # https://www.youtube.com/watch?v=lIpev8JXJHQ
        def fmt_print_arg(self, value: Any, /) -> str:
            return 'Malkovich'

    repl = MaklovichRepl()
    repl_eval = repl.run_code("print(1, 2, 3)")
    assert repl_eval.output == 'Malkovich Malkovich Malkovich\n'


def verify_display_hook():
    class AngryRepl(BaseRepl):
        def fmt_display_arg(self, value: Any, /) -> str:
            return repr(value).upper()

    repl = AngryRepl()
    repl_eval = repl.run_code("'ok'")
    assert repl_eval.out_value == 'ok'
    assert repl_eval.out_str == "'OK'"
    assert repl_eval.output == "'OK'\n"

    repl_eval = repl.run_code("def foo(): pass")
    assert not repl_eval.has_out_value
    assert repl_eval.out_str is None


def verify_exception_hook():
    exceptions = set()

    class MyRepl(BaseRepl):
        def on_uncaught_exception(self, evaluation, error, /) -> None:
            exceptions.add(type(error.exception))

    repl = MyRepl()
    repl.run_code("1 / 0")
    repl.run_code("foo")
    repl.run_code("{}[1]")
    assert exceptions == {ZeroDivisionError, NameError, KeyError}


def verify_import_hook():
    imports = []

    class MyRepl(BaseRepl):
        def on_import(self, evaluation, name, items) -> None:
            imports.append((name, items))

    repl = MyRepl()
    ev = repl.run_code('''
    import builtins
    import time
    from math import sqrt
    ''')
    assert ev.error is None
    assert ev.output == ''
    assert ev.imported == ['builtins', 'time', 'math']
    assert imports == [
        ('builtins', None),
        ('time', None),
        ('math', ('sqrt',)),
    ]


if __name__ == '__main__':
    verify_print_hook()
    verify_display_hook()
    verify_exception_hook()
    verify_import_hook()
