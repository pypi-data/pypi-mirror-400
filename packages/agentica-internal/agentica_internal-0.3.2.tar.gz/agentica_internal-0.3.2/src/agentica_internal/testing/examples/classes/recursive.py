# fmt: off

from collections.abc import Iterable
from typing import Self

__all__ = [
    'AnyChain',
    'AnyTree',
    'AnyNat',
    'Chain',
    'ChainLink',
    'ChainEnd',
    'Tree',
    'TreeNode',
    'TreeLeaf',
    'Nat',
    'NatOdd',
    'NatEven',
    'NatZero',
    'RECURSIVE_CLASSES',
    'RECURSIVE_ALIASES',
]


class Chain:
    """Chain docstring"""

    def step(self) -> Self: ...


class ChainLink(Chain):
    """ChainLink docstring"""

    n: Chain

    def __init__(self, n: Chain):
        self.n = n

    def step(self) -> Chain:
        return self.n


class ChainEnd(Chain):
    """ChainEnd docstring"""

    def __init__(self): ...

    def step(self) -> Self:
        return self


class Tree:
    """Tree docstring"""

    def leaves(self) -> Iterable['TreeLeaf']: ...


class TreeNode(Tree):
    """TreeNode docstring"""

    l: Tree
    r: Tree

    def __init__(self, l: Tree, r: Tree):
        self.l = l
        self.r = r

    def leaves(self) -> Iterable['TreeLeaf']:
        yield from self.l.leaves()
        yield from self.r.leaves()


class TreeLeaf(Tree):
    """TreeLeaf docstring"""

    def __init__(self): ...

    def leaves(self) -> Iterable['TreeLeaf']:
        yield self


class Nat:
    """Nat docstring"""
    i: int

    def __init__(self, i: int):
        self.i = i

    def dec(self) -> Self: ...
    def inc(self) -> Self: ...


class NatOdd(Nat):
    """NatOdd docstring"""

    def dec(self) -> 'NatEven':
        return NatEven(self.i - 1) if self.i > 1 else NatZero(0)

    def inc(self) -> 'NatEven':
        return NatEven(self.i + 1)


class NatEven(Nat):
    """NatEven docstring"""

    def dec(self) -> 'NatOdd | NatZero':
        return NatOdd(self.i - 1)

    def inc(self) -> NatOdd:
        return NatOdd(self.i + 1)


class NatZero(Nat):
    """NatZero docstring"""

    def __init__(self):
        super().__init__(0)

    def dec(self) -> Self: ...
    def inc(self) -> NatEven: ...


type AnyChain = ChainLink | ChainEnd
type AnyTree = TreeNode | TreeLeaf
type AnyNat = NatOdd | NatEven | NatZero


RECURSIVE_CLASSES: list[type] = [
    Chain,
    ChainLink,
    ChainEnd,
    Tree,
    TreeNode,
    TreeLeaf,
    Nat,
    NatOdd,
    NatEven,
    NatZero,
]

RECURSIVE_ALIASES: list = [AnyChain, AnyTree, AnyNat]

RECURSIVE_INSTANCES: list = [
    ChainEnd(),
    ChainLink(ChainEnd()),
    ChainLink(ChainLink(ChainEnd())),
    TreeLeaf(),
    TreeNode(TreeLeaf(), TreeLeaf()),
    TreeNode(TreeNode(TreeLeaf(), TreeLeaf()), TreeLeaf()),
    NatZero(),
    NatOdd(1),
    NatEven(2),
]
