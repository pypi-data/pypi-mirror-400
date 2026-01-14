import msgspec
from agentica_internal.warpc.worlds.debug_world import DebugWorld

world = DebugWorld(name='world')
other_world = DebugWorld(name='other_world')


class ClsWithAttr:
    my_attr: str | None

    def __init__(self):
        self.my_attr = 'foo'


my_class = ClsWithAttr()

test_fiddlings: list[str | int] = ["one", 2, "three", 4, "five", 6, "seven", 8, "nine", 10]


def processIntersection(obj: ClsWithAttr) -> str:
    return "foo"


json_encoder = msgspec.json.Encoder()
msg = world.root.enc_any(processIntersection)
print([json_encoder.encode(ctx_def) for ctx_def in world.root.outgoing_defs])
