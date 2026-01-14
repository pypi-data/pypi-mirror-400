from agentica_internal.repl.repl import *


def verify_delta_added():
    repl = BaseRepl()
    repl_eval = repl.run_code('''
    x = 5
    ''')
    assert repl_eval.locals_delta.delta_str() == '+x'


def verify_delta_changed():
    repl = BaseRepl()
    repl.update_locals({'x': 1, 'y': 2, 'z': [], 'i': 0})
    repl_eval = repl.run_code('''
    i += 1       # same as i = i + 1
    x = 1        # new is not old
    y = 20       # new is not old
    z = []       # new == old, but is not old
    ''')
    assert repl_eval.locals_delta.delta_str() == '~i ~y ~z'


def verify_delta_removed():
    repl = BaseRepl()
    repl.update_locals({'x': 1, 'y': 2, 'z': 3})
    repl_eval = repl.run_code('''
    del x         # just removed         = -x
    y = 0; del y  # changed then removed = -y  
    q = 0; del q  # added then removed   = nothing
    del z; z = 1  # removed then added   = ~z
    ''')
    assert repl_eval.locals_delta.delta_str() == '-x -y ~z'


if __name__ == '__main__':
    verify_delta_added()
    verify_delta_changed()
    verify_delta_removed()
