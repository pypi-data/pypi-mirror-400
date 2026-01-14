from typing import Any

from agentica_internal.repl.repl import *


def verify_fmt_print():
    class MaklovichRepl(BaseRepl):
        # https://www.youtube.com/watch?v=lIpev8JXJHQ

        def fmt_print(self, args, sep, end) -> str:
            return 'Malkovich? ' + super().fmt_print(args, sep, end)

        def fmt_print_arg(self, value: Any, /) -> str:
            return 'Malkovich!'

    repl = MaklovichRepl(logging=False)
    repl_eval = repl.run_code("print(1, 2, 3)")
    assert repl_eval.output == 'Malkovich? Malkovich! Malkovich! Malkovich!\n'


def verify_fmt_display():
    class AngryRepl(BaseRepl):
        def fmt_display_arg(self, value: Any, /) -> str:
            return repr(value).upper()

    repl = AngryRepl()
    ev = repl.run_code("'ok'")
    assert ev.out_value == 'ok'
    assert ev.out_str == "'OK'"
    assert ev.output == "'OK'\n"

    ev = repl.run_code("def foo(): pass")
    assert not ev.has_out_value


def verify_fmt_exception():
    class MyRepl(BaseRepl):
        def fmt_exception_tb(self, exception, /) -> str:
            return 'an exception occurred'

    repl = MyRepl(logging=False)
    ev = repl.run_code('''
    print(1)
    1 / 0
    print(2)
    ''')
    assert ev.output == '1\nan exception occurred\n'


if __name__ == '__main__':
    verify_fmt_print()
    verify_fmt_display()
    verify_fmt_exception()
