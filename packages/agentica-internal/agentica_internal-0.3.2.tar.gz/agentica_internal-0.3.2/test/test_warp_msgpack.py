# ruff: noqa
# fmt: off

import pytest
from agentica_internal.testing.warpc.msgpack_tests import verify_msgpack_tests


@pytest.mark.skip("bizarre CI-only issue")  # TODO: Investigate
def test_warp_msgpack(request):
    verify_msgpack_tests(pytest_request=request)
