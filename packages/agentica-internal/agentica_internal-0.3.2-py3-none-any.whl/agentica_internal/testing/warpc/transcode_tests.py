# fmt: off

from typing import *

from agentica_internal.testing import *
from agentica_internal.testing.examples import ANNOS, CLASSES
from agentica_internal.warpc.worlds.debug_world import DebugWorld


def transcode_msg(v: Any):
    world = DebugWorld(world_id=9, logging=False)
    frame = world.root
    enc_context = frame.enc_context()
    with enc_context:
        msg = world.codec.enc_any(v)
    defs = enc_context.enc_context_defs()
    return msg.msgpack_str() + '\n' + '\n'.join(d.msgpack_str() for d in defs)


class MyThing:
    pass


MyThing.__module__ = 'my_module'

my_thing = MyThing()

CUSTOM = [
    [my_thing, my_thing, my_thing],
]

file = FileTemplate(__file__, '{kind}.json', section='{name}')


def verify_msgpack_tests(pytest_request=None):
    objects = ANNOS + CLASSES + CUSTOM
    run_object_to_file_tests(
        dump_msg, objects, results_file=file, on_error='e', pytest_request=pytest_request
    )


if __name__ == '__main__':
    verify_msgpack_tests()
