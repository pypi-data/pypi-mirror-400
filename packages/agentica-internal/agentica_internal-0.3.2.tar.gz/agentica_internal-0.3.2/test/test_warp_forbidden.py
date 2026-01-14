import pytest
from agentica_internal.testing.warpc.forbidden_tests import *


@pytest.mark.asyncio
async def test_forbidden_module():
    await verify_forbidden_module()


@pytest.mark.asyncio
async def test_forbidden_whitelist():
    await verify_forbidden_whitelist()
