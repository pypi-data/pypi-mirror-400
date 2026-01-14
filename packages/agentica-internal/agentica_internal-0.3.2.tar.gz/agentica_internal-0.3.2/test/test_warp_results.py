# ruff: noqa
# fmt: off

import pytest

from agentica_internal.testing.warpc.result_tests import verify_error_result, EXCEPTIONS


@pytest.mark.asyncio
@pytest.mark.parametrize('exception', EXCEPTIONS)
async def test_warp_type_annotation(exception):
    verify_error_result(exception)
