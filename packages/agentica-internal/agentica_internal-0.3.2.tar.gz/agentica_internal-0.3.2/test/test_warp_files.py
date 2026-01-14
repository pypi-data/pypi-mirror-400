# ruff: noqa
# fmt: off

import pytest
from agentica_internal.testing.warpc.virtual_file_tests import *


@pytest.mark.asyncio
async def test_virtual_path():
    await verify_virtual_path()

@pytest.mark.asyncio
async def test_text_write_via_virtual_file():
    await verify_text_write_via_virtual_file()

@pytest.mark.asyncio
async def test_text_read_via_virtual_file():
    await verify_text_read_via_virtual_file()
