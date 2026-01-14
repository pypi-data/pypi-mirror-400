# fmt: off

import enum
import datetime as DT
import dataclasses as DC
import itertools as IT
import inspect as INS
import re as RE
import warnings
import os
import copyreg

from ...core.anno import union_iter

from .__ import *
from .term import *
from .msg_aliases import *


__all__ = [
    'SlotObjMsg',
    'ReduceObjMsg',
    'RegexPatternMsg',
    'RegexMatchMsg',
    'ClassUnionMsg',
    'EnumMemberMsg',
    'EnumKeyMsg',
    'EnumValMsg'
]


################################################################################

if TYPE_CHECKING:
    from .term_resource import ResourceMsg, SystemResourceMsg

################################################################################

type SlotObjT = DC.Field | DC._DataclassParams | DC.InitVar  # type: ignore

SLOT_OBJ_TYPES: tuple[type, ...] = SlotObjT.__value__.__args__  # type: ignore


################################################################################

class SlotObjMsg(TermPassByValMsg, tag='slots'):
    """Message describing objects by-value via their slot contents. Used
    for instances of certain builtin system classes that we wish to serialize by-value, like
    dataclass Fields."""

    type V = SlotObjT

    cls: 'SystemResourceMsg'
    slots: 'Rec[TermMsg]'

    def __len__(self) -> int:
        return len(self.slots)

    def __shape__(self) -> str:
        return self.cls.sys_name

    def decode(self, dec: DecoderP) -> V:
        from .term_resource import SystemResourceMsg
        assert isinstance(self.cls, SystemResourceMsg)
        _cls = self.cls.sys_cls
        term = object.__new__(_cls)  # type: ignore
        slots = dec.dec_record(self.slots)
        for slot_key, slot_val in slots.items():
            setattr(term, slot_key, slot_val)
        return term

    @classmethod
    def encode_compound(cls, term: V, enc: EncoderP) -> 'SlotObjMsg':
        _cls = type(term)
        slot_keys = _cls.__slots__
        cls_msg = enc.enc_class(_cls)
        assert isinstance(cls_msg, SystemResourceMsg), f"trying to encode non-system cls {_cls}"
        slots, add_slot = mkdict()
        enc_any = enc.enc_any
        for slot_key in slot_keys:
            val = getattr(term, slot_key, FIELD_ABSENT)
            if val is not FIELD_ABSENT:
                add_slot(slot_key, enc_any(val))
        return SlotObjMsg(cls_msg, slots)


################################################################################

type ReducibleBuiltinsObjT = (
    partial | range | map | filter | zip
)

type ReducibleItertoolsObjT = (
    IT.count | IT.islice | IT.cycle | IT.repeat | IT.takewhile | IT.dropwhile |
    IT.zip_longest | IT.starmap
)

type ReducibleOSObjT = (
    os.stat_result
)

type ReducibleDatetimeObjT = (
    DT.date | DT.time | DT.datetime | DT.timedelta
)

type ReducibleInspectObjT = (
    INS.Signature | INS.Parameter | INS.BoundArguments
)

type ReducibleObjT = (
    ReducibleBuiltinsObjT
    | ReducibleItertoolsObjT
    | ReducibleInspectObjT
    | ReducibleOSObjT
    | ReducibleDatetimeObjT
)

REDUCIBLE_TYPES: tuple[type, ...] = tuple(union_iter(ReducibleObjT, type))

################################################################################

class ReduceObjMsg(TermPassByValMsg, tag='reduce'):
    """Message describing objects by-value via the result of `__reduce__`."""

    type V = ReducibleObjT

    cls: 'SystemResourceMsg'
    args: 'Tup[TermMsg]'
    state: 'TermMsg | None'

    def __shape__(self) -> str:
        return self.cls.sys_name

    def decode(self, dec: DecoderP) -> V:
        assert isinstance(self.cls, SystemResourceMsg)
        _cls = self.cls.sys_resource  # might be a class, or 'iter', which is a function
        if _cls not in REDUCIBLE_TYPES:
            raise E.WarpDecodingError(f"{_cls!r} is not reducible")
        args = dec.dec_sequence(self.args)
        state = dec.dec_any(self.state) if self.state is not None else None
        try:
            obj = _cls(*args)
            obj.__setstate__(state) if state is not None else None
            return obj
        except BaseException as exc:
            raise E.WarpDecodingError(f"Could not expand {self}:\n{exc!r}")

    @classmethod
    def encode_compound(cls, term: V, enc: EncoderP) -> 'ReduceObjMsg':
        _cls = type(term)
        try:
            reduced = term.__reduce__()
            if len(reduced) == 2:
                clb, args = reduced
                assert clb is not copyreg._reconstructor
                state = None
            elif len(reduced) == 3:
                clb, args, state = reduced
            else:
                raise E.WarpEncodingError(f"bad reduction: {f_object_id(reduced)}")
            # assert clb is _cls, f"constructor is not original type: {clb} != {_cls}"
            assert type(args) is tuple, f"args is not a tuple: {f_object_id(args)}"
        except BaseException as exc:
            # f_exc = fmt_exception(exc)
            raise E.WarpEncodingError(f"Could not reduce {f_object_id(term)}: {exc}")
        cls_msg = enc.enc_system_resource(_cls)
        args_msg = enc.enc_sequence(args)
        state_msg = enc.enc_any(state)
        return ReduceObjMsg(cls_msg, args_msg, state_msg)


################################################################################

class RegexPatternMsg(TermPassByValMsg, tag='regex_pattern'):
    """Message describing re.Pattern objects by value."""

    type V = RE.Pattern

    pattern: str
    flags:   int

    def decode(self, dec: DecoderP) -> V:
        return RE._compile(self.pattern, self.flags)

    @classmethod
    def encode_atom(cls, term: V) -> 'RegexPatternMsg':
        return RegexPatternMsg(term.pattern, term.flags)


################################################################################

class RegexMatchMsg(TermPassByValMsg, tag='regex_match'):
    """Message describing re.Match objects by value."""

    type V = RE.Match

    pattern: str
    flags:   int
    string:  str
    span:   tuple[int, int]

    def decode(self, dec: DecoderP) -> V:
        # this is ugly but since re.Match is not pickle-able there is
        # no other way to do it!
        patt = RE._compile(self.pattern, self.flags)
        start, end = span = self.span
        for match in patt.finditer(self.string, start, end):
            if match.span() == span:
                return match
        raise E.WarpDecodingError(f"Could not reconstruct re.Match")

    @classmethod
    def encode_atom(cls, term: V) -> 'RegexMsg':
        re = term.re
        return RegexMatchMsg(re.pattern, int(re.flags), term.string, term.span())


################################################################################

class ClassUnionMsg(TermPassByValMsg, tag='class_union'):
    """Message for simple inline unions like `int | float` (used by typescript for 'Number')."""

    alts: 'ClassesTupleMsg'

    def decode(self, dec: DecoderP) -> TypeT:
        try:
            cls_list = []
            for msg in self.alts:
                cls = dec.dec_type(msg)
                if not isinstance(cls, type):
                    return Any
            union = cls_list[0]
            for cls in cls_list[1:]:
                union |= cls
            return union
        except:
            return Any


################################################################################

class EnumMemberMsg(TermPassByValMsg):

    cls: 'ResourceMsg'

    def decode(self, dec: DecoderP) -> enum.Enum: ...

    @staticmethod
    def encode_enum(value: enum.Enum, enc: EncoderP) -> 'EnumMemberMsg':
        cls_msg = enc.enc_class(type(value))
        if isinstance(value, int):
            # IntFlags in particular allow non-nameable enum values
            return EnumValMsg(cls_msg, enc.enc_any(int(value)))
        else:
            return EnumKeyMsg(cls_msg, value.name)


################################################################################

class EnumKeyMsg(EnumMemberMsg, tag='enum_key'):

    cls: 'ResourceMsg'
    key:  str

    def decode(self, dec: DecoderP) -> TypeT:
        enum_cls = dec.dec_class(self.cls)
        if not issubclass(enum_cls, enum.Enum):
            raise E.WarpEncodingError(f"{enum_cls=!r} is not an enum class")
        return enum_cls._member_map_[self.key]


################################################################################

class EnumValMsg(EnumMemberMsg, tag='enum_val'):

    cls: 'ResourceMsg'
    val: 'TermMsg'

    def decode(self, dec: DecoderP) -> TypeT:
        enum_cls = dec.dec_class(self.cls)
        enum_val = dec.dec_any(self.val)
        if not issubclass(enum_cls, enum.Enum):
            raise E.WarpEncodingError(f"{enum_cls=!r} is not an enum class")
        return enum_cls(enum_val)


################################################################################

# FIXME: replace this mechanism with virtual iterators
warnings.filterwarnings(
    'ignore',
    message='Pickle, copy, and deepcopy support will be removed from itertools in Python 3.14.',
    category=DeprecationWarning,
    append=True
)
