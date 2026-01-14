# ruff: noqa
# fmt: off

import pytest

from agentica_internal.testing.warpc.virtual_class_tests import verify_user_class, verify_generic_class
from agentica_internal.testing.warpc.virtual_dataclass_tests import verify_data_class, verify_empty_data_class


@pytest.mark.asyncio
async def test_warp_generic_class():
    await verify_generic_class()


@pytest.mark.asyncio
async def test_warp_user_class():
    await verify_user_class()


@pytest.mark.asyncio
async def test_warp_data_class():
    await verify_data_class()


@pytest.mark.asyncio
async def test_warp_empty_data_class():
    await verify_empty_data_class()
