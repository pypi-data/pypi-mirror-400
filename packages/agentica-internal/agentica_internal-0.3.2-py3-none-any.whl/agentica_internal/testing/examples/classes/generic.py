# fmt: off

__all__ = [
    'GENERIC_CLASSES'
]

class GenericClass[X]:

    def generic_method(self) -> X: ...


GENERIC_CLASSES = [GenericClass]
