# fmt: off

import enum
import sys

__all__ = [
    'SysModule',
    'SysClassID',
    'SysObjectID',
    'SysFunctionID',
    'SYS_MOD_TABLE',
    'SYS_CLASS_ID_DICT',
    'SYS_OBJECT_ID_DICT',
    'SYS_FUNCTION_ID_DICT',
]

###############################################################################

PY13 = sys.version_info >= (3, 13)


class SysModule(enum.StrEnum):
    B = 'builtins'
    S = 'types'
    X = 'agentica_internal.cpython.iters'
    Z = 'agentica_internal.core.sentinels'
    J = 'agentica_internal.javascript'
    JS = 'json'
    A = 'abc'
    T = 'typing'
    C = 'collections'
    CA = 'collections.abc'
    CF = 'concurrent.futures'
    AI = 'asyncio'
    AIE = 'asyncio.exceptions'
    AIQ = 'asyncio.queues'
    EN = 'enum'
    DC = 'dataclasses'
    IT = 'itertools'
    FT = 'functools'
    IN = 'inspect'
    IO = 'io'
    RE = 're'
    OS = 'os'
    OP = 'operator'
    DT = 'datetime'
    RAND = 'random'


SYS_MOD_TABLE: list[tuple[int, str, str]]
SYS_MOD_TABLE = [(i, k, str(v)) for i, (k, v) in enumerate(SysModule.__members__.items())]


###############################################################################


class SysClassID(enum.IntEnum):
    """
    Names some builtin types and orders them in a sane way.
    Various types are grouped in ranges that are meaningful in hex.

    These enums can be processed to build tables.

    The keys here are prefixed by the module in which the type can be found; see ModuleID.

    The hex ranges used are:

    00X | immutable datums  | int, bool, ...
    01X | containers        | list, tuple, ...
    02X | collections.*     | defaultdict, deque, ...
    03X | proxy containers  | MappingProxyType, ...
    04X | iterators         | types of iter([]), iter({}), ...
    05X | callables         | FunctionType, MethodType,...
    06x | types.*           | ModuleType, FrameType, ...
    07x | builtins.*        | property, staticmethod, map, filter, ...

    0EX | typing            | Any, NewType, ...

    1XX | abcs              | ABC, Iterable, ...
    2XX | protocols         | Protocol, SupportsInt, ...
    30X | enums             | Enum, EnumInt, ...
    31X | dataclasses       | Field, InitVar, ...
    32X | re                | Pattern, Match
    33X | datetime          | date, datetime, time, ...
    40X | itertools         | chain, ...
    50X | functools         | partial, partialmethod, ...
    51X | operator          | partial, partialmethod, ...
    6XX | io                | IOBase, FileIO, ...

    EXX | typing internals  | Any, NewType, ...
    FXX | exceptions        | BaseException, Exception, ...
    """

    B_bool                           = 0x01   # immutable datums
    B_int                            = 0x02
    B_float                          = 0x03
    B_complex                        = 0x04
    B_str                            = 0x05
    B_bytes                          = 0x06
    S_NoneType                       = 0x0A
    S_EllipsisType                   = 0x0B
    S_NotImplementedType             = 0x0C
    B_tuple                          = 0x10
    B_list                           = 0x11   # containers
    B_set                            = 0x12
    B_dict                           = 0x13
    B_frozenset                      = 0x14
    B_bytearray                      = 0x15
    B_memoryview                     = 0x16
    C_ChainMap                       = 0x20   # collections
    C_Counter                        = 0x21
    C_defaultdict                    = 0x22
    C_deque                          = 0x23
    C_OrderedDict                    = 0x24
    S_MappingProxyType               = 0x30   # proxy containers
    if PY13:
        X_FrameLocalsProxyType       = 0x31
    X_DictKeysType                   = 0x32
    X_DictValuesType                 = 0x33
    X_DictItemsType                  = 0x34
    X_DictKeysIterType               = 0x40   # iterators
    X_DictValuesIterType             = 0x41
    X_DictItemsIterType              = 0x42
    X_ListIterType                   = 0x43
    X_TupleIterType                  = 0x44
    X_SetIterType                    = 0x45
    X_ReversedListIterType           = 0x47
    X_StrIterType                    = 0x4A
    X_BytesIterType                  = 0x4B
    X_ByteArrayIterType              = 0x4C
    X_CallableIterType               = 0x4D
    S_FunctionType                   = 0x50   # callable CPython types
    S_BuiltinFunctionType            = 0x51
    S_MethodType                     = 0x52
    S_MethodDescriptorType           = 0x53
    S_WrapperDescriptorType          = 0x54
    S_MethodWrapperType              = 0x55
    S_ClassMethodDescriptorType      = 0x56
    S_CodeType                       = 0x57
    S_ModuleType                     = 0x60   # core CPython types
    S_SimpleNamespace                = 0x61
    S_CellType                       = 0x64
    S_CoroutineType                  = 0x65
    S_GeneratorType                  = 0x66
    S_AsyncGeneratorType             = 0x67
    S_GetSetDescriptorType           = 0x68
    S_MemberDescriptorType           = 0x69
    S_FrameType                      = 0x6A
    S_TracebackType                  = 0x6B
    B_property                       = 0x70   # other builtin types
    B_staticmethod                   = 0x71
    B_classmethod                    = 0x72
    B_super                          = 0x73
    B_slice                          = 0x74
    B_enumerate                      = 0x75
    B_range                          = 0x76
    B_filter                         = 0x77
    B_map                            = 0x78
    B_zip                            = 0x79
    B_reversed                       = 0x80
    T_Any                            = 0xE0   # public typing.* types
    T_Generic                        = 0xE1
    # S_UnionType                    = 0xE2
    # S_GenericAlias                 = 0xE3
    T_ForwardRef                     = 0xE4
    T_NewType                        = 0xE5
    T_TypeVar                        = 0xE6
    T_TextIO                         = 0xE7
    T_BinaryIO                       = 0xE8
    B_object                         = 0xF0   # basic
    B_type                           = 0xFF
    A_ABC                            = 0x100  # ABCs
    CA_Hashable                      = 0x101
    CA_Awaitable                     = 0x102
    CA_Coroutine                     = 0x103
    CA_AsyncIterable                 = 0x104
    CA_AsyncIterator                 = 0x105
    CA_AsyncGenerator                = 0x106
    CA_Iterable                      = 0x107
    CA_Iterator                      = 0x108
    CA_Reversible                    = 0x109
    CA_Generator                     = 0x10A
    CA_Sized                         = 0x10B
    CA_Container                     = 0x10C
    CA_Collection                    = 0x10D
    CA_Buffer                        = 0x10E
    CA__CallableGenericAlias         = 0x10F
    CA_Callable                      = 0x110
    CA_Set                           = 0x111
    CA_MutableSet                    = 0x112
    CA_Mapping                       = 0x114
    CA_MappingView                   = 0x115
    CA_KeysView                      = 0x116
    CA_ItemsView                     = 0x117
    CA_ValuesView                    = 0x118
    CA_MutableMapping                = 0x119
    CA_Sequence                      = 0x11A
    CA_ByteString                    = 0x11B
    CA_MutableSequence               = 0x11C
    A_ABCMeta                        = 0x1F0
    T_Protocol                       = 0x200  # protocols
    T_SupportsInt                    = 0x201
    T_SupportsFloat                  = 0x202
    T_SupportsComplex                = 0x203
    T_SupportsBytes                  = 0x204
    T_SupportsIndex                  = 0x205
    T_SupportsAbs                    = 0x206
    T_SupportsRound                  = 0x207
    EN_Enum                          = 0x300  # enums
    EN_IntEnum                       = 0x301
    EN_StrEnum                       = 0x302
    EN_Flag                          = 0x303
    EN_ReprEnum                      = 0x304
    if PY13:
        EN_EnumDict                  = 0x30C  # internal types
    EN_EnumType                      = 0x30D
    EN_auto                          = 0x30E
    # EN_EnumMeta                      = 0x30F
    DC_Field                         = 0x310  # dataclasses
    DC_InitVar                       = 0x311
    DC__DataclassParams              = 0x312
    RE_Pattern                       = 0x320  # re
    RE_Match                         = 0x321
    DT_date                          = 0x330  # datetime
    DT_datetime                      = 0x331
    DT_time                          = 0x332
    DT_timedelta                     = 0x333
    DT_tzinfo                        = 0x334
    DT_timezone                      = 0x335
    IT_accumulate                    = 0x400  # itertools
    IT_batched                       = 0x401
    IT_chain                         = 0x402
    IT_combinations                  = 0x403
    IT_combinations_with_replacement = 0x404
    IT_compress                      = 0x405
    IT_count                         = 0x406
    IT_cycle                         = 0x407
    IT_dropwhile                     = 0x408
    IT_filterfalse                   = 0x409
    IT_groupby                       = 0x40A
    IT_islice                        = 0x40B
    IT_pairwise                      = 0x40C
    IT_permutations                  = 0x40D
    IT_product                       = 0x40E
    IT_repeat                        = 0x40F
    IT_starmap                       = 0x410
    IT_takewhile                     = 0x411
    IT_zip_longest                   = 0x412
    FT_partial                       = 0x500  # functools
    FT_partialmethod                 = 0x501
    FT_singledispatchmethod          = 0x502
    FT_cached_property               = 0x503
    OP_attrgetter                    = 0x510  # operator types
    OP_itemgetter                    = 0x511
    OP_methodcaller                  = 0x512
    IO_IOBase                        = 0x600  # io
    IO_RawIOBase                     = 0x601
    IO_FileIO                        = 0x602
    IO_BytesIO                       = 0x603
    IO_StringIO                      = 0x604
    IO_BufferedIOBase                = 0x605
    IO_BufferedReader                = 0x606
    IO_BufferedWriter                = 0x607
    IO_BufferedRWPair                = 0x608
    IO_BufferedRandom                = 0x609
    IO_TextIOBase                    = 0x610
    IO_TextIOWrapper                 = 0x611
    IN_BoundArguments                = 0x700  # inspect
    IN_BufferFlags                   = 0x701
    IN_Parameter                     = 0x702
    IN_Signature                     = 0x703
    IN__void                         = 0x7F0
    IN__empty                        = 0x7F1
    IN__ParameterKind                = 0x7F2
    AI_Future                        = 0x800  # asyncio
    AI_Task                          = 0x801
    AI_Event                         = 0x802
    AIQ_Queue                        = 0x803
    AI_AbstractEventLoop             = 0x810
    OS_stat_result                   = 0x900  # os
    RAND_Random                      = 0xA00  # random
    RAND_SystemRandom                = 0xA01
    T__SpecialForm                   = 0xE11  # internal typing.* types / metas
    T__BaseGenericAlias              = 0xE12
    T__GenericAlias                  = 0xE13
    T__SpecialGenericAlias           = 0xE14
    T__DeprecatedGenericAlias        = 0xE15
    T__CallableGenericAlias          = 0xE16
    T__CallableType                  = 0xE17
    T__TupleType                     = 0xE18
    T__UnionGenericAlias             = 0xE19
    T__LiteralGenericAlias           = 0xE1A
    T__ConcatenateGenericAlias       = 0xE1B
    T__UnpackGenericAlias            = 0xE1C
    T__TypingEllipsis                = 0xE1D
    T__AnnotatedAlias                = 0xE1F
    T__IdentityCallable              = 0xE20
    T__Final                         = 0xE22
    T__NotIterable                   = 0xE23
    T_NamedTupleMeta                 = 0xEF0
    T__AnyMeta                       = 0xEF1
    T__TypedDictMeta                 = 0xEF2
    T__ProtocolMeta                  = 0xEF3
    B_BaseException                  = 0xF00  # builtin exceptions
    B_Exception                      = 0xF01
    B_GeneratorExit                  = 0xF02
    B_KeyboardInterrupt              = 0xF03
    B_SystemExit                     = 0xF04
    B_StopIteration                  = 0xF05
    B_OSError                        = 0xF06
    B_ArithmeticError                = 0xF07
    B_AssertionError                 = 0xF08
    B_AttributeError                 = 0xF09
    B_BufferError                    = 0xF0A
    B_EOFError                       = 0xF0B
    B_ImportError                    = 0xF0C
    B_LookupError                    = 0xF0D
    B_MemoryError                    = 0xF0E
    B_NameError                      = 0xF0F
    B_ReferenceError                 = 0xF10
    B_RuntimeError                   = 0xF11
    B_StopAsyncIteration             = 0xF12
    B_SyntaxError                    = 0xF13
    B_SystemError                    = 0xF14
    B_TypeError                      = 0xF15
    B_ValueError                     = 0xF16
    B_FloatingPointError             = 0xF17
    B_OverflowError                  = 0xF18
    B_ZeroDivisionError              = 0xF19
    B_ModuleNotFoundError            = 0xF1A
    B_IndexError                     = 0xF1B
    B_KeyError                       = 0xF1C
    B_UnboundLocalError              = 0xF1D
    B_BlockingIOError                = 0xF1E
    B_ChildProcessError              = 0xF1F
    B_ConnectionError                = 0xF20
    B_BrokenPipeError                = 0xF21
    B_ConnectionAbortedError         = 0xF22
    B_ConnectionRefusedError         = 0xF23
    B_ConnectionResetError           = 0xF24
    B_FileExistsError                = 0xF25
    B_FileNotFoundError              = 0xF26
    B_InterruptedError               = 0xF27
    B_IsADirectoryError              = 0xF28
    B_NotADirectoryError             = 0xF29
    B_PermissionError                = 0xF2A
    B_ProcessLookupError             = 0xF2B
    B_TimeoutError                   = 0xF2C
    B_NotImplementedError            = 0xF2D
    B_RecursionError                 = 0xF2E
    B_IndentationError               = 0xF2F
    B_TabError                       = 0xF30
    B_UnicodeError                   = 0xF31
    B_UnicodeDecodeError             = 0xF32
    B_UnicodeEncodeError             = 0xF33
    B_UnicodeTranslateError          = 0xF34
    B_Warning                        = 0xF35
    B_UserWarning                    = 0xF36
    B_DeprecationWarning             = 0xF37
    B_SyntaxWarning                  = 0xF38
    B_RuntimeWarning                 = 0xF39
    B_FutureWarning                  = 0xF3A
    B_PendingDeprecationWarning      = 0xF3B
    B_ImportWarning                  = 0xF3C
    B_UnicodeWarning                 = 0xF3D
    B_BytesWarning                   = 0xF3E
    B_ResourceWarning                = 0xF3F
    AI_CancelledError                = 0xFA1
    AI_InvalidStateError             = 0xFA2
    CF_CancelledError                = 0xFA4
    CF_BrokenExecutor                = 0xFA5  # wrong module?
    JS_JSONDecodeError               = 0xFA6
    IO_UnsupportedOperation          = 0xFA0
    DC_FrozenInstanceError           = 0xFA1
    IN_ClassFoundException           = 0xFA2
    IN_EndOfBlock                    = 0xFA3


SYS_CLASS_ID_DICT: dict[str, int] = {v._name_: v._value_ for v in SysClassID}

###############################################################################


class SysObjectID(enum.IntEnum):
    B_None                           = 0x00
    B_NotImplemented                 = 0x01
    B_Ellipsis                       = 0x02  # `typing.X` equivalents of `builtins.X`
    T_Tuple                          = 0x10
    T_List                           = 0x11
    T_Set                            = 0x12
    T_Dict                           = 0x13
    T_FrozenSet                      = 0x14  # `typing.X` equivalents of `builtins.X`
    T_ChainMap                       = 0x20
    T_Counter                        = 0x21
    T_DefaultDict                    = 0x22
    T_Deque                          = 0x23
    T_OrderedDict                    = 0x24
    T_Type                           = 0xFF
    T_Hashable                       = 0x101  # `typing.X` equivalents of `collections.abc.X`
    T_Awaitable                      = 0x102
    T_Coroutine                      = 0x103
    T_AsyncIterable                  = 0x104
    T_AsyncIterator                  = 0x105
    T_AsyncGenerator                 = 0x106
    T_Iterable                       = 0x107
    T_Iterator                       = 0x108
    T_Reversible                     = 0x109
    T_Generator                      = 0x10A
    T_Sized                          = 0x10B
    T_Container                      = 0x10C
    T_Collection                     = 0x10D
    T_Callable                       = 0x110
    T_MutableSet                     = 0x112
    T_Mapping                        = 0x114
    T_MappingView                    = 0x115
    T_KeysView                       = 0x116
    T_ItemsView                      = 0x117
    T_ValuesView                     = 0x118
    T_MutableMapping                 = 0x119
    T_Sequence                       = 0x11A
    T_ByteString                     = 0x11B
    T_MutableSequence                = 0x11C

    RAND__inst                       = 0x200  # random default state

    DC__HAS_DEFAULT_FACTORY          = 0xE00  # dataclass sentinels
    DC_MISSING                       = 0xE01
    DC_KW_ONLY                       = 0xE02
    DC__EMPTY_METADATA               = 0xE03
    DC__FIELD                        = 0xE04
    DC__FIELD_CLASSVAR               = 0xE05
    DC__FIELD_INITVAR                = 0xE06
    IN_POSITIONAL_ONLY               = 0xE10  # inspect sentinels
    IN_POSITIONAL_OR_KEYWORD         = 0xE11
    IN_VAR_POSITIONAL                = 0xE12
    IN_KEYWORD_ONLY                  = 0xE13
    IN_VAR_KEYWORD                   = 0xE14
    Z_PENDING                        = 0xEE0
    Z_CLOSED                         = 0xEE1
    Z_CANCELED                       = 0xEE2
    Z_ERRORED                        = 0xEE3
    Z_ARG_DEFAULT                    = 0xEE4
    IN__is_coroutine_mark            = 0xC00
    IN__is_coroutine_marker          = 0xC00  # I'm SURE this existed in 3.12.0
    T_NoReturn                       = 0xF00  # special forms
    T_Never                          = 0xF01
    T_Self                           = 0xF02
    T_LiteralString                  = 0xF03
    T_Union                          = 0xF04
    T_Optional                       = 0xF05
    T_Unpack                         = 0xF06
    T_Literal                        = 0xF07
    T_TypeAlias                      = 0xF08
    T_Concatenate                    = 0xF09
    T_ClassVar                       = 0xF10
    T_Final                          = 0xF11
    T_Required                       = 0xF12
    T_NotRequired                    = 0xF13
    if PY13:
        T_ReadOnly                   = 0xF14
    T_TypeGuard                      = 0xF15
    if PY13:
        T_TypeIs                     = 0xF16
    J_Number                         = 0xFF0  # javascript equivalents


SYS_OBJECT_ID_DICT: dict[str, int] = {v._name_: v._value_ for v in SysObjectID}

###############################################################################


class SysFunctionID(enum.IntEnum):
    B_abs                            = 0x0000
    B_aiter                          = 0x0001
    B_all                            = 0x0002
    B_anext                          = 0x0003
    B_any                            = 0x0004
    B_ascii                          = 0x0005
    B_bin                            = 0x0006
    B_breakpoint                     = 0x0007
    B_callable                       = 0x0008
    B_chr                            = 0x0009
    B_compile                        = 0x000A
    B_delattr                        = 0x000B
    B_dir                            = 0x000C
    B_divmod                         = 0x000D
    B_eval                           = 0x000E
    B_exec                           = 0x000F
    B_format                         = 0x0010
    B_getattr                        = 0x0011
    B_globals                        = 0x0012
    B_hasattr                        = 0x0013
    B_hash                           = 0x0014
    B_hex                            = 0x0015
    B_id                             = 0x0016
    B_input                          = 0x0017
    B_isinstance                     = 0x0018
    B_issubclass                     = 0x0019
    B_iter                           = 0x001A
    B_len                            = 0x001B
    B_locals                         = 0x001C
    B_max                            = 0x001D
    B_min                            = 0x001E
    B_next                           = 0x001F
    B_oct                            = 0x0020
    B_open                           = 0x0021
    B_ord                            = 0x0022
    B_pow                            = 0x0023
    B_print                          = 0x0024
    B_repr                           = 0x0025
    B_round                          = 0x0026
    B_setattr                        = 0x0027
    B_sorted                         = 0x0028
    B_sum                            = 0x0029
    B_vars                           = 0x002A
    S_coroutine                      = 0x0100
    S_get_original_bases             = 0x0101
    S_new_class                      = 0x0102
    S_prepare_class                  = 0x0103
    S_resolve_bases                  = 0x0104
    A_abstractmethod                 = 0x0300
    A_get_cache_token                = 0x0301
    A_update_abstractmethods         = 0x0302
    T_NamedTuple                     = 0x0400
    T_TypedDict                      = 0x0401
    T_assert_never                   = 0x0402
    T_assert_type                    = 0x0403
    T_cast                           = 0x0404
    T_clear_overloads                = 0x0405
    T_dataclass_transform            = 0x0406
    T_final                          = 0x0407
    T_get_args                       = 0x0408
    T_get_origin                     = 0x0409
    T_get_overloads                  = 0x040A
    T_get_type_hints                 = 0x040B
    T_is_typeddict                   = 0x040C
    T_no_type_check                  = 0x040D
    T_no_type_check_decorator        = 0x040E
    T_overload                       = 0x040F
    T_override                       = 0x0410
    T_reveal_type                    = 0x0411
    T_runtime_checkable              = 0x0412
    C_namedtuple                     = 0x0500
    AI_all_tasks                     = 0x0700
    AI_as_completed                  = 0x0701
    AI_create_eager_task_factory     = 0x0702
    AI_create_subprocess_exec        = 0x0703
    AI_create_subprocess_shell       = 0x0704
    AI_create_task                   = 0x0705
    AI_current_task                  = 0x0706
    AI_eager_task_factory            = 0x0707
    AI_ensure_future                 = 0x0708
    AI_gather                        = 0x0709
    AI_get_child_watcher             = 0x070A
    AI_get_event_loop                = 0x070B
    AI_get_event_loop_policy         = 0x070C
    AI_get_running_loop              = 0x070D
    AI_iscoroutine                   = 0x070E
    AI_iscoroutinefunction           = 0x070F
    AI_isfuture                      = 0x0710
    AI_new_event_loop                = 0x0711
    AI_open_connection               = 0x0712
    AI_open_unix_connection          = 0x0713
    AI_run                           = 0x0714
    AI_run_coroutine_threadsafe      = 0x0715
    AI_set_child_watcher             = 0x0716
    AI_set_event_loop                = 0x0717
    AI_set_event_loop_policy         = 0x0718
    AI_shield                        = 0x0719
    AI_sleep                         = 0x071A
    AI_start_server                  = 0x071B
    AI_start_unix_server             = 0x071C
    AI_timeout                       = 0x071D
    AI_timeout_at                    = 0x071E
    AI_to_thread                     = 0x071F
    AI_wait                          = 0x0720
    AI_wait_for                      = 0x0721
    AI_wrap_future                   = 0x0722
    EN_global_enum                   = 0x0800
    EN_global_enum_repr              = 0x0801
    EN_global_flag_repr              = 0x0802
    EN_global_str                    = 0x0803
    EN_pickle_by_enum_name           = 0x0804
    EN_pickle_by_global_name         = 0x0805
    EN_unique                        = 0x0806
    DC_asdict                        = 0x0900
    DC_astuple                       = 0x0901
    DC_dataclass                     = 0x0902
    DC_field                         = 0x0903
    DC_fields                        = 0x0904
    DC_is_dataclass                  = 0x0905
    DC_make_dataclass                = 0x0906
    DC_replace                       = 0x0907
    IT_tee                           = 0x0A00
    FT_cache                         = 0x0B00
    FT_cmp_to_key                    = 0x0B01
    FT_lru_cache                     = 0x0B02
    FT_reduce                        = 0x0B03
    FT_singledispatch                = 0x0B04
    FT_total_ordering                = 0x0B05
    FT_update_wrapper                = 0x0B06
    FT_wraps                         = 0x0B07
    IN_classify_class_attrs          = 0x0C00
    IN_cleandoc                      = 0x0C01
    IN_currentframe                  = 0x0C02
    IN_findsource                    = 0x0C03
    IN_formatannotation              = 0x0C04
    IN_formatannotationrelativeto    = 0x0C05
    IN_formatargvalues               = 0x0C06
    IN_get_annotations               = 0x0C07
    IN_getabsfile                    = 0x0C08
    IN_getargs                       = 0x0C09
    IN_getargvalues                  = 0x0C0A
    IN_getasyncgenlocals             = 0x0C0B
    IN_getasyncgenstate              = 0x0C0C
    IN_getattr_static                = 0x0C0D
    IN_getblock                      = 0x0C0E
    IN_getcallargs                   = 0x0C0F
    IN_getclasstree                  = 0x0C10
    IN_getclosurevars                = 0x0C11
    IN_getcomments                   = 0x0C12
    IN_getcoroutinelocals            = 0x0C13
    IN_getcoroutinestate             = 0x0C14
    IN_getdoc                        = 0x0C15
    IN_getfile                       = 0x0C16
    IN_getframeinfo                  = 0x0C17
    IN_getfullargspec                = 0x0C18
    IN_getgeneratorlocals            = 0x0C19
    IN_getgeneratorstate             = 0x0C1A
    IN_getinnerframes                = 0x0C1B
    IN_getlineno                     = 0x0C1C
    IN_getmembers                    = 0x0C1D
    IN_getmembers_static             = 0x0C1E
    IN_getmodule                     = 0x0C1F
    IN_getmodulename                 = 0x0C20
    IN_getmro                        = 0x0C21
    IN_getouterframes                = 0x0C22
    IN_getsource                     = 0x0C23
    IN_getsourcefile                 = 0x0C24
    IN_getsourcelines                = 0x0C25
    IN_indentsize                    = 0x0C26
    IN_isabstract                    = 0x0C27
    IN_isasyncgen                    = 0x0C28
    IN_isasyncgenfunction            = 0x0C29
    IN_isawaitable                   = 0x0C2A
    IN_isbuiltin                     = 0x0C2B
    IN_isclass                       = 0x0C2C
    IN_iscode                        = 0x0C2D
    IN_iscoroutine                   = 0x0C2E
    IN_iscoroutinefunction           = 0x0C2F
    IN_isdatadescriptor              = 0x0C30
    IN_isframe                       = 0x0C31
    IN_isfunction                    = 0x0C32
    IN_isgenerator                   = 0x0C33
    IN_isgeneratorfunction           = 0x0C34
    IN_isgetsetdescriptor            = 0x0C35
    IN_ismemberdescriptor            = 0x0C36
    IN_ismethod                      = 0x0C37
    IN_ismethoddescriptor            = 0x0C38
    IN_ismethodwrapper               = 0x0C39
    IN_ismodule                      = 0x0C3A
    IN_isroutine                     = 0x0C3B
    IN_istraceback                   = 0x0C3C
    IN_markcoroutinefunction         = 0x0C3D
    IN_signature                     = 0x0C3E
    IN_stack                         = 0x0C3F
    IN_trace                         = 0x0C40
    IN_unwrap                        = 0x0C41
    IN_walktree                      = 0x0C42
    IO_open_code                     = 0x0D00
    RE_compile                       = 0x0E00
    RE_escape                        = 0x0E01
    RE_findall                       = 0x0E02
    RE_finditer                      = 0x0E03
    RE_fullmatch                     = 0x0E04
    RE_match                         = 0x0E05
    RE_purge                         = 0x0E06
    RE_search                        = 0x0E07
    RE_split                         = 0x0E08
    RE_sub                           = 0x0E09
    RE_subn                          = 0x0E0A
    if not PY13: # RE_template was removed in Python 3.13
        RE_template                  = 0x0E0B
    OP_abs                           = 0x0F00
    OP_add                           = 0x0F01
    OP_and_                          = 0x0F02
    OP_call                          = 0x0F03
    OP_concat                        = 0x0F04
    OP_contains                      = 0x0F05
    OP_countOf                       = 0x0F06
    OP_delitem                       = 0x0F07
    OP_eq                            = 0x0F08
    OP_floordiv                      = 0x0F09
    OP_ge                            = 0x0F0A
    OP_getitem                       = 0x0F0B
    OP_gt                            = 0x0F0C
    OP_iadd                          = 0x0F0D
    OP_iand                          = 0x0F0E
    OP_iconcat                       = 0x0F0F
    OP_ifloordiv                     = 0x0F10
    OP_ilshift                       = 0x0F11
    OP_imatmul                       = 0x0F12
    OP_imod                          = 0x0F13
    OP_imul                          = 0x0F14
    OP_index                         = 0x0F15
    OP_indexOf                       = 0x0F16
    OP_inv                           = 0x0F17
    OP_invert                        = 0x0F18
    OP_ior                           = 0x0F19
    OP_ipow                          = 0x0F1A
    OP_irshift                       = 0x0F1B
    OP_is_                           = 0x0F1C
    OP_is_not                        = 0x0F1D
    OP_isub                          = 0x0F1E
    OP_itruediv                      = 0x0F1F
    OP_ixor                          = 0x0F20
    OP_le                            = 0x0F21
    OP_length_hint                   = 0x0F22
    OP_lshift                        = 0x0F23
    OP_lt                            = 0x0F24
    OP_matmul                        = 0x0F25
    OP_mod                           = 0x0F26
    OP_mul                           = 0x0F27
    OP_ne                            = 0x0F28
    OP_neg                           = 0x0F29
    OP_not_                          = 0x0F2A
    OP_or_                           = 0x0F2B
    OP_pos                           = 0x0F2C
    OP_pow                           = 0x0F2D
    OP_rshift                        = 0x0F2E
    OP_setitem                       = 0x0F2F
    OP_sub                           = 0x0F30
    OP_truediv                       = 0x0F31
    OP_truth                         = 0x0F32
    OP_xor                           = 0x0F33
    RAND_seed                        = 0x1000  # random bound methods
    RAND_random                      = 0x1001
    RAND_uniform                     = 0x1002
    RAND_triangular                  = 0x1003
    RAND_randint                     = 0x1004
    RAND_choice                      = 0x1005
    RAND_randrange                   = 0x1006
    RAND_sample                      = 0x1007
    RAND_shuffle                     = 0x1008
    RAND_choices                     = 0x1009
    RAND_normalvariate               = 0x100A
    RAND_lognormvariate              = 0x100B
    RAND_expovariate                 = 0x100C
    RAND_vonmisesvariate             = 0x100D
    RAND_gammavariate                = 0x100E
    RAND_gauss                       = 0x100F
    RAND_betavariate                 = 0x1010
    RAND_binomialvariate             = 0x1011
    RAND_paretovariate               = 0x1012
    RAND_weibullvariate              = 0x1013
    RAND_getstate                    = 0x1014
    RAND_setstate                    = 0x1015
    RAND_getrandbits                 = 0x1016
    RAND_randbytes                   = 0x1017

SYS_FUNCTION_ID_DICT: dict[str, int] = {v._name_: v._value_ for v in SysFunctionID}


# the above is generated by:
def _generate_function_ids():
    from importlib import import_module

    from agentica_internal.cpython.alias import CALLABLES as FUNC_TYPES

    seen = set()
    see = seen.add
    for i, prefix, name in SYS_MOD_TABLE:
        mod = import_module(name)
        j = i << 8
        items = list(vars(mod).items())
        exports = getattr(mod, '__all__', None)
        items.sort()
        for k, v in items:
            if k.startswith('_'):
                continue
            if exports and k not in exports:
                continue
            if isinstance(v, FUNC_TYPES):
                i = id(v)
                if i in seen:
                    continue
                see(i)
                name = f'{prefix}_{k}'
                print('    ', name.ljust(33), '= ', f'0x{j:04X}', sep='')
                j += 1
