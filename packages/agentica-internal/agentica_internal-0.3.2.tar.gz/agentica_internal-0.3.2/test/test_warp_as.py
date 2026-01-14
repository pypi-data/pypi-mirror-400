import pytest
from agentica_internal.testing.warpc.virtual_warp_as_tests import *


@pytest.mark.asyncio
async def test_warp_as():
    await verify_warp_as()


@pytest.mark.asyncio
async def test_class_warp_as():
    await verify_class_warp_as()
