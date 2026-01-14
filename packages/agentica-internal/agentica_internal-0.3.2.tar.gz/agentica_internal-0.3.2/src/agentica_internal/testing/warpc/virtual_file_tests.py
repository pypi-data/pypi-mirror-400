# fmt: off

import asyncio

from agentica_internal.warpc.worlds.debug_world import *


async def verify_virtual_path():


    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair as B:

        path = pair.tmp_file
        path.write_text("data")

        path_b = await B(path)
        assert is_virtual(path_b)
        assert path_b.exists()
        assert path_b.read_bytes() == b"data"
        assert path_b.read_bytes() == b"data"



async def verify_text_write_via_virtual_file():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair as B:

        path = pair.tmp_file
        with open(path.as_posix(), 'w') as file:
            assert file.write('aaa') == 3
            file_b = await B(file)
            assert is_virtual(file_b)
            assert file.write('xxx') == 3

        assert path.exists()
        assert path.read_text() == 'aaaxxx'


async def verify_text_read_via_virtual_file():

    pair = DebugWorld.connected_pair(logging=False, qualify_names=False)
    async with pair as B:

        path = pair.tmp_file
        path.write_text('yyy')
        with open(path.as_posix(), 'r') as file:
            file_b = await B(file)
            assert is_virtual(file_b)
            assert file.readline() == 'yyy'
            assert file.seek(0) == 0
            assert file.readline() == 'yyy'


if __name__ == '__main__':
    asyncio.run(verify_virtual_path())
    asyncio.run(verify_text_write_via_virtual_file())
    asyncio.run(verify_text_read_via_virtual_file())
