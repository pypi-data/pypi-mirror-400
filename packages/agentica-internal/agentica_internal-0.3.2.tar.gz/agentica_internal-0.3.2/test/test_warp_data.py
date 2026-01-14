# ruff: noqa
# fmt: off

import pytest

from agentica_internal.testing.warpc.virtual_data_tests import verify_plain_old_data


@pytest.mark.asyncio
async def test_warp_plain_old_data():
    await verify_plain_old_data()
