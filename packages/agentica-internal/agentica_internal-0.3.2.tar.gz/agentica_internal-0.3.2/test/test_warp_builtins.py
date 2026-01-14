# ruff: noqa
# fmt: off

import pytest

from agentica_internal.testing.warpc.virtual_builtin_tests import verify_virtual_queue


@pytest.mark.asyncio
async def test_virtual_queue():
    await verify_virtual_queue()
