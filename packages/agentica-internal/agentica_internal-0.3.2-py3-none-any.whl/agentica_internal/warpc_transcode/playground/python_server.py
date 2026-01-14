from __future__ import annotations

import asyncio as aio

from agentica_internal.core.print import tprint
from agentica_internal.warpc.messages import DefinitionMsg, RPCMsg
from agentica_internal.warpc.repl import DummyRepl
from agentica_internal.warpc.worlds.sdk_world import SDKWorld
from agentica_internal.warpc_transcode.playground.toy_translator import Translator


async def main() -> None:
    translator = Translator()

    async def TS_recv_bytes() -> bytes:
        msg: RPCMsg = await aio.to_thread(translator.recv_py_rpc, 1000)
        tprint("Really received Python RPCMsg:", msg)
        return msg.to_msgpack()

    async def TS_send_bytes(data: bytes) -> None:
        tprint("TS_send_bytes", data)
        msg = RPCMsg.from_msgpack(data)
        tprint("Preparing to send Python RPCMsg:", msg)
        await aio.to_thread(translator.send_py_rpc, msg)

    sandbox = SDKWorld(logging=True)
    sandbox.attach_repl(DummyRepl())

    # Init REPL with meaning
    if translator.init:
        print("Initializing REPL with", translator.init)
        decoded: dict[str, object] = {}
        for name, res_def in translator.init.items():
            if isinstance(res_def, DefinitionMsg):
                decoded[name] = sandbox.frames.root.dec_any(res_def)
        repl = DummyRepl()
        sandbox.attach_repl(repl)
        repl.set_global_vars(decoded)
        print("REPL Initialized with", decoded)

    print("Sandbox after init:", sandbox)

    # Call meaning
    assert sandbox.frames.repl is not None
    meaning = sandbox.frames.repl.get_var("meaningOfLife")
    sandbox.event_loop = aio.get_running_loop()
    async with aio.TaskGroup() as tg:
        tg.create_task(sandbox.drain_outbox(TS_send_bytes))
        tg.create_task(sandbox.fill_inbox(TS_recv_bytes))
        tg.create_task(sandbox.process_inbox(tg))

        def _call_meaning():
            with sandbox.frames.root:
                return meaning()  # type: ignore

        result = await aio.to_thread(_call_meaning)
        tprint("Result:", result)


if __name__ == "__main__":
    aio.run(main())
