# EXCLUDE_FROM_SDK_BUILD
# fmt: off

from ..__ import *

from copy import copy
from pathlib import Path

from agentica_internal.cpython.alias import *
from agentica_internal.cpython.shed.load import get_shed_class, get_shed_module
from agentica_internal.warpc.attrs import *

from agentica_internal.warpc.resource.virtual_function import make_template_strs, describe_real_function

type OClass = type
type SClass = type
type VClass = type

type Kind = Literal['i', 'c', 's']
type Methods = dict[str, tuple[FunctionT, Kind]]


def is_func(func: Any) -> TypeGuard[FunctionT]:
    return type(func) is FunctionType


SELF_REF = f"get_raw(self, '{VHDL}')"
TYPE_REF = f"get_raw(type(self), '{VHDL}')"
CLS_REF = f"get_raw(self, '{VHDL}')"


class MethodInfo:
    name: str
    func: FunctionType
    kind: Kind
    code: str

    DROP: str = ''

    def __init__(self, func: Callable, code: str):
        assert is_func(func)
        self.name = func.__name__
        self.func = func
        self.code = code

    def __repr__(self) -> str:
        f_cls = type(self).__name__
        return f'{f_cls}({self.name!r}, {self.code!r})'

    @staticmethod
    def from_shed(func: Callable) -> 'MethodInfo':
        cls = type(func)
        func = getattr(func, '__wrapped__', func)
        code = getattr(func, '___shed_src___')
        info = TO_METHOD_INFO_CLS[cls](func, code)
        info.fixup()
        return info

    def to_virtual(self, cls_name: str) -> 'MethodInfo':
        v_info = copy(self)
        fn_def = describe_real_function(self.func)
        if type(self) is not SMethodInfo:
            if fn_def.pos_args:
                fn_def.pos_args = fn_def.pos_args[1:]
            elif fn_def.args:
                fn_def.args = fn_def.args[1:]
        _, pos_str, key_str = make_template_strs(fn_def)
        args_str = f'{pos_str}, {key_str}'
        args = pos_str[1:-1].split(', ')
        v_callback_str = self.v_callback_str(cls_name, args_str, *args)
        v_info.code = replace_ellipsis(self.code, v_callback_str)
        return v_info

    def v_callback_str(self, cls_name: str, args_str: str, *args: str) -> str: ...

    def fixup(self):
        pass


SPECIAL = (
    '__setattr__',
    '__getattr__',
    '__delattr__',
)

SYS_METHODS = {
    '__str__': 'str',
    '__len__': 'len',
    '__iter__': 'iter',
    '__aiter__': 'aiter',
    '__next__': 'next',
    '__anext__': 'anext',
    '__repr__': 'str',
    '__hash__': 'hash',
    '__copy__': 'copy',
}


class IMethodInfo(MethodInfo):
    def v_callback_str(self, cls_name: str, args_str: str, *args) -> str:
        return f"return v_callback('callmethod', {SELF_REF}, '{self.name}', {args_str})"

    def fixup(self):
        if self.name in SPECIAL:
            self.__class__ = CustomMethodInfo
        if sys_meth := SYS_METHODS.get(self.name):
            self.__class__ = SysMethodInfo
            self.sys_meth = sys_meth


class CMethodInfo(MethodInfo):
    def v_callback_str(self, cls_name: str, args_str: str, *args) -> str:
        return f"return v_callback('callmethod', {CLS_REF}, {args_str})"


class SMethodInfo(MethodInfo):
    def v_callback_str(self, cls_name: str, args_str: str, *args) -> str:
        return 'raise NotImplementedError()'

    def fixup(self):
        if self.name == '__new__':
            self.__class__ = CustomMethodInfo


class CustomMethodInfo(MethodInfo):
    def v_callback_str(self, cls_name: str, args_str: str, *args: str) -> str:
        match self.name:
            case '__new__':
                return f"return v_callback('new', {CLS_REF}, {args_str})"
            case '__setattr__':
                return f"return v_callback('setattr', {SELF_REF}, {args[0]}, {args[1]})"
            case '__getattr__':
                return f"return v_callback('getattr', {SELF_REF}, {args[0]})"
            case '__delattr__':
                return f"return v_callback('delattr', {SELF_REF}, {args[0]})"
        raise ValueError(self)


class SysMethodInfo(MethodInfo):
    sys_meth: str

    def v_callback_str(self, cls_name: str, args_str: str, *strs) -> str:
        return f"return v_callback('callsysmethod', {SELF_REF}, {self.sys_meth})"


TO_METHOD_INFO_CLS = {
    FunctionT: IMethodInfo,
    classmethod: CMethodInfo,
    staticmethod: SMethodInfo,
}


def replace_ellipsis(code: str, body: str) -> str:
    *most, last = code.rstrip(' \n\t').rsplit('\n', 1)
    last = last.removesuffix('...')
    margin = last.split('def', 1)[0]
    most = '\n'.join(most)
    return f'{most}\n{last}\n{margin}    {body}'


class ClassInfo:
    cls: OClass
    name: str
    module: str | None
    rename: str | None
    bases: tuple[str, ...]
    meths: dict[str, MethodInfo]
    slots: tuple[str, ...] | None

    def __init__(self, cls: OClass, name: str, module: str | None):
        self.cls = cls
        self.name = name
        self.module = module
        self.meths = {}
        self.bases = ()
        self.module = module
        self.rename = None
        self.slots = None

    def __repr__(self) -> str:
        return f'ClassInfo({self.name!r}, {self.bases!r}, {self.meths!r})'

    @staticmethod
    def from_shed(s_cls: SClass) -> 'ClassInfo':
        o_cls = s_cls.___shed_ori___
        info = ClassInfo(o_cls, o_cls.__name__, o_cls.__module__)
        info.bases = tuple(b.__name__ for b in o_cls.__bases__)
        info.slots = getattr(o_cls, '__slots__', None)
        add = info.meths.__setitem__
        for key, val in s_cls.__dict__.items():
            if key in IGNORE:
                continue
            if isinstance(val, (FunctionType, classmethod, staticmethod)):
                m_info = MethodInfo.from_shed(val)
                add(key, m_info)
        return info

    def update(self, other: 'ClassInfo') -> None:
        self.meths.update(other.meths)

    def to_virtual(self) -> Self:
        s_name = self.name
        v_name = 'virtual_' + s_name
        v_info = ClassInfo(self.cls, v_name, self.module)
        v_info.bases = (s_name,)
        v_info.meths = {k: v.to_virtual(s_name) for k, v in self.meths.items()}
        v_info.rename = s_name
        return v_info

    def code(self) -> str:
        return '\n\n'.join(self.codelines())

    def codelines(self):
        bases = ', '.join(self.bases)
        name = self.name
        yield f'class {self.name}({bases}):'
        if slots := self.slots:
            yield f'    __slots__ = {slots!r}'
        for meth in self.meths.values():
            yield meth.code
        if rename := self.rename:
            yield f'{name}.__name__ = {name}.__qualname__ = {rename!r}'
        if module := self.module:
            yield f'{name}.__module__ = {module!r}'


class SClassInfo(dict[OClass, ClassInfo]):
    def __missing__(self, key: OClass) -> ClassInfo:
        return self.add_class(key)

    def add_class(self, cls: OClass) -> ClassInfo:
        s_cls = get_shed_class(cls)
        s_info = ClassInfo.from_shed(s_cls)
        self[cls] = s_info
        for base in s_cls.__bases__:
            b_info = SCLASS_INFO[base]
            s_info.update(b_info)
        return s_info


class VClassInfo(dict[SClass, ClassInfo]):
    def __missing__(self, key: OClass) -> ClassInfo:
        return self.add_class(key)

    def add_class(self, cls: OClass) -> ClassInfo:
        s_info = SCLASS_INFO[cls]
        v_info = s_info.to_virtual()
        self[cls] = v_info
        return v_info


IGNORE = (
    '__init_subclass__',
    '__init__',
    '__getattribute__',
    '__reduce__',
    '__reduce_ex__',
    '__getstate__',
    # type
    '__prepare__',
    '__subclasscheck__',
    '__subclasshook__',
    '__sizeof__',
    '__subclasses__',
    'mro',
)

SCLASS_INFO = SClassInfo()
VCLASS_INFO = VClassInfo()


def generate():
    this_dir = Path(__file__).parent
    builtins_mod = get_shed_module('builtins')

    out_file = this_dir / 'generated.py'

    v_blocks, add_block = mklist()
    add_block('from .common import *')

    for cls in [object, type, list, set]:
        v_info = VCLASS_INFO[cls]
        v_code = v_info.code()

        P.hprint(v_code)
        add_block(v_code)

    out_file.write_text('\n\n'.join(v_blocks))


generate()
