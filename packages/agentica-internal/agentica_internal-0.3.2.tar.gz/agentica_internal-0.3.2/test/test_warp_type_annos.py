# ruff: noqa
# fmt: off

import pytest

from agentica_internal.testing.examples.annos import TreeAlias
from agentica_internal.testing.warpc.type_anno_tests import (
    ANNOS,
    CLASSES,
    verify_annotation_equality,
    verify_class_annotation_equality,
    verify_normalizing_unions
)


@pytest.mark.asyncio
@pytest.mark.parametrize('annotation', ANNOS)
async def test_warp_type_annotation(annotation):
    if annotation is TreeAlias:
        pytest.skip()
    await verify_annotation_equality(annotation)


@pytest.mark.asyncio
@pytest.mark.parametrize('cls', CLASSES)
async def test_warp_class_annotation(cls):
    await verify_class_annotation_equality(cls)


def test_warp_normalizing_unions():
    verify_normalizing_unions()
