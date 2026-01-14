from agentica_internal.warpc.msg.term_lambda import (
    function_to_lambda_msg,
    lambda_msg_to_function,
    lambda_msg_to_source,
)
from agentica_internal.warpc.pure import PURE_CODEC

fn = lambda x: int(x) if x else [5]

msg = function_to_lambda_msg(PURE_CODEC, fn)
msg.pprint()

fn2 = lambda_msg_to_function(PURE_CODEC, msg)
assert fn(0) == fn2(0)
assert fn(1) == fn2(1)


def f(): ...


fn = lambda x, y, z: x + y + str(z)

print(type(fn), fn.__name__)
msg = function_to_lambda_msg(PURE_CODEC, fn)
msg.pprint()

print(lambda_msg_to_source(PURE_CODEC, msg))
fn2 = lambda_msg_to_function(PURE_CODEC, msg)
print(fn2('a', 'b', 55))
