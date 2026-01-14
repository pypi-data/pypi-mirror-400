# fmt: off

__all__ = [
    'unbound_instance_method',
    'bound_instance_method',
    'bound_class_method',
    'builtin_bound_class_method',
    'builtin_bound_instance_method',
    'builtin_bound_dunder_method',
    'builtin_bound_dunder_method',
    'METHODS',
]

class Class:
    """Class docstring"""

    def instance_method(self, inst_method_arg: object) -> str:
        """Class.inst_method docstring"""
        ...

    @staticmethod
    def static_method(static_method_arg: bytes) -> object:
        """Class.static_method docstring"""
        ...

    @classmethod
    def class_method(cls, class_method_arg: int) -> int:
        """Class.class_method docstring"""
        ...

obj = Class()

unbound_instance_method = Class.instance_method
bound_instance_method = obj.instance_method
bound_class_method = Class.class_method
builtin_bound_class_method = bytes.hex
builtin_bound_instance_method = bytes().__buffer__
builtin_unbound_dunder_method = Class.__str__
builtin_bound_dunder_method = obj.__str__

METHODS = [
    unbound_instance_method,
    bound_instance_method,
    bound_class_method,
    builtin_bound_class_method,
    builtin_bound_instance_method,
    builtin_unbound_dunder_method,
    builtin_bound_dunder_method,
]
