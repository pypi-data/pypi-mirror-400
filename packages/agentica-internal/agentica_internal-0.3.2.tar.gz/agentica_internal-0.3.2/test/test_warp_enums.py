# ruff: noqa
# fmt: off

import pytest

from agentica_internal.testing.examples.annos import TreeAlias
from agentica_internal.testing.warpc.virtual_enum_tests import (
    ENUM_CLASSES,
    ENUM_INSTANCES,
    verify_enum_cls,
    verify_enum_obj,
)


@pytest.mark.asyncio
@pytest.mark.parametrize('enum_cls', ENUM_CLASSES)
async def test_warp_enum_class(enum_cls):
    await verify_enum_cls(enum_cls)


@pytest.mark.asyncio
@pytest.mark.parametrize('obj', ENUM_INSTANCES)
async def test_warp_enum_object(obj):
    await verify_enum_obj(obj)
