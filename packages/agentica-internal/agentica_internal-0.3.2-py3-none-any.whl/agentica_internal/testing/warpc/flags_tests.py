from agentica_internal.warpc import flags
from agentica_internal.warpc.messages import *
from agentica_internal.warpc.msg import system as SYS


def verify_inline_definitions():
    obj_msg = ObjectDataMsg(cls=SYS.OBJECT, keys=('a',))
    def_msg = DefinitionMsg(rid=(1, 1, 1), data=obj_msg)
    list_msg = ListMsg(vs=(def_msg,))
    data = list_msg.to_msgpack()

    try:
        msg = TermMsg.from_msgpack(data)
    except BaseException as exc:
        print(exc)
        msg = None

    if flags.INLINE_DEFINITIONS:
        assert msg is not None, "inline def incorrectly forbidden"
    else:
        assert msg is None, "inline def incorrectly allowed"


if __name__ == "__main__":
    verify_inline_definitions()
