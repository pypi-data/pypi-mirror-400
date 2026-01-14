# ruff: noqa
# fmt: off

import pytest
from agentica_internal.testing.warpc.func_default_tests import *


@pytest.mark.asyncio
async def test_no_func_defaults():
    await verify_no_func_defaults()

@pytest.mark.asyncio
async def test_atom_func_defaults():
    await verify_atom_func_defaults()

@pytest.mark.asyncio
async def test_all_func_defaults():
    await verify_all_func_defaults()
