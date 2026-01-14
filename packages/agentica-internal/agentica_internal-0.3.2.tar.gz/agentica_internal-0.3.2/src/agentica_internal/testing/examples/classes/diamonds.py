# fmt: off

__all__ = [
    'DiamondC',
    'DiamondT',
    'DiamondB',
    'DiamondL',
    'DiamondR',
    'DiamondBL',
    'DiamondBR',
    'DiamondTL',
    'DiamondTR',
    'DIAMOND_CLASSES',
    'DIAMOND_INSTANCES',
]

type NEG = None
type POS = None
type ZER = None


class DiamondC:
    """DiamondC docsting"""

    x: ZER
    y: ZER


class DiamondB(DiamondC): y: NEG
class DiamondT(DiamondC): y: POS
class DiamondL(DiamondC): x: NEG
class DiamondR(DiamondC): x: POS

class DiamondBL(DiamondB, DiamondL): pass
class DiamondBR(DiamondB, DiamondR): pass
class DiamondTL(DiamondT, DiamondL): pass
class DiamondTR(DiamondT, DiamondR): pass

DIAMOND_CLASSES: list[type] = [
    DiamondC,
    DiamondT,
    DiamondB,
    DiamondL,
    DiamondR,
    DiamondBL,
    DiamondBR,
    DiamondTL,
    DiamondTR,
]

DIAMOND_INSTANCES: list[object] = [
    DiamondC(),
    DiamondT(),
    DiamondB(),
    DiamondL(),
    DiamondR(),
    DiamondBL(),
    DiamondBR(),
    DiamondTL(),
    DiamondTR(),
]
