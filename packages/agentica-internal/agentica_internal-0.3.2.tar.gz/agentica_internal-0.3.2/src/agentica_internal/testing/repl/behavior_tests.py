from agentica_internal.repl.repl import *


def verify_stdout_capture():
    repl = BaseRepl()
    data = repl.run_code('''
    import sys
    import io
    sys.stdout = buffer = io.StringIO()
    print('hello')
    captured = buffer.getvalue()
    ''')
    assert not data.has_error
    captured = repl.vars.locals['captured']
    assert isinstance(captured, str)
    assert captured == 'hello\n'


if __name__ == '__main__':
    verify_stdout_capture()
