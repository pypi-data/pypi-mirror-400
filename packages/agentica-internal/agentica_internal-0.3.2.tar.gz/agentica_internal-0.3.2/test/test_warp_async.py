# ruff: noqa
# fmt: off

import pytest
from agentica_internal.testing.warpc.async_coro_tests import *
from agentica_internal.testing.warpc.async_future_tests import *
from agentica_internal.testing.warpc.virtual_future_tests import *


@pytest.mark.asyncio
async def test_coro_function():
    await verify_coro_function()


@pytest.mark.asyncio
async def test_coro_functions_run_concurrently():
    await verify_coro_functions_run_concurrently()


@pytest.mark.asyncio
async def test_future_function_ok():
    await verify_future_function_ok()


@pytest.mark.asyncio
async def test_future_function_error():
    await verify_future_function_error()


@pytest.mark.asyncio
async def test_virtual_future_properties():
    await verify_virtual_future_properties()


@pytest.mark.asyncio
async def test_virtual_cancellation():
    await verify_virtual_cancellation()


@pytest.mark.asyncio
async def test_virtual_completion():
    await verify_virtual_completion()


@pytest.mark.asyncio
async def test_real_cancellation():
    await verify_real_cancellation()


@pytest.mark.asyncio
async def test_real_completion():
    await verify_real_completion()
