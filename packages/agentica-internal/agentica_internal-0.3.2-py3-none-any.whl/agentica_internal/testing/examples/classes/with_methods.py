# fmt: off

__all__ = [
    'MethodClassBase',
    'MethodClass',
    'MethodClassSub',
    'WITH_METHOD_CLASSES',
    'WITH_METHOD_INSTANCES',
]


class MethodClassBase:
    def __init__(self, init_arg: int):
        """MethodClassBase.__init__ docstring"""
        ...

    def inst_method(self, inst_method_arg: str) -> object:
        """MethodClassBase.inst_method docstring"""
        ...

    @classmethod
    def class_method(cls, class_method_arg: bool) -> object:
        """MethodClassBase.class_method docstring"""
        ...


class MethodClass(MethodClassBase):
    """MethodClass docstring"""

    def __init__(self, init_arg: object):
        """MethodClass.__init__ docstring"""
        ...

    def inst_method(self, inst_method_arg: object) -> str:
        """MethodClass.inst_method docstring"""
        ...

    @staticmethod
    def static_method(static_method_arg: bytes) -> object:
        """MethodClass.static_method docstring"""
        ...

    @classmethod
    def class_method(cls, class_method_arg: int) -> int:
        """MethodClass.class_method docstring"""
        ...


class MethodClassSub(MethodClass):
    """MethodClassSub docstring"""

    def __init__(self, init_arg: object, *int_args, **init_kwargs):
        """MethodClassSub.__init__ docstring"""
        ...

    @classmethod
    def class_method(cls, class_method_arg: object) -> bool:
        """MethodClassSub.class_method docstring"""
        ...


WITH_METHOD_CLASSES: list[type] = [
    MethodClassBase,
    MethodClass,
    MethodClassSub,
]

WITH_METHOD_INSTANCES: list[object] = [
    MethodClassBase(0),
    MethodClass(0),
    MethodClassSub(0),
]
