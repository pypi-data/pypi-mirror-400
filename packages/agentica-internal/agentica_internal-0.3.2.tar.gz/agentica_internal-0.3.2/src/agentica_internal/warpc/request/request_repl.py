# fmt: off

import re

from ..repl import ReplP

from .__ import *
from .base import Request

__all__ = [
    'ReplRequest',
    'ReplInit',
    'ReplRunCode',
    'ReplCallMethod',
]


################################################################################

if TYPE_CHECKING:
    from ...repl.repl_eval_info import ReplEvaluationInfo

################################################################################


class ReplRequest(Request, ABC):
    """
    ABC for a fully decoded REPL request.
    """

    __slots__ = __match_args__ = ('repl',)

    repl: 'ReplP'

    ############################################################################

    def __fmt_args__(self):
        for slot in self.__slots__[1:]:
            yield f_object_id(getattr(self, slot, FIELD_ABSENT))

    ############################################################################

    def execute(self) -> Result:
        log = bool(LOG_REPL)
        if not hasattr(self, "repl"):
            P.nprint(ICON_E, 'no repl present') if log else None
            return Result.bad(RuntimeError("no repl present"))
        try:
            val = self.__execute__(log)
            res = Result.good(val)
        except E.WarpError as err:
            P.nprint(ICON_E, err, sep='\n') if log else None
            res = Result.bad(RuntimeError(f"internal error: {err}"))
        except BaseException as err:
            P.nprint(ICON_E, err, sep='') if log else None
            res = Result.bad(err)
        P.nprint(ICON_O, res, '\n') if log else None
        return res

    @abstractmethod
    def __execute__(self, log: bool) -> TermT: ...

    ############################################################################

    async def execute_async(self) -> Result:
        log = bool(LOG_REPL)
        if not hasattr(self, "repl"):
            P.nprint(ICON_E, 'no repl present') if log else None
            return Result.bad(RuntimeError("no repl present"))
        try:
            val = await self.__execute_async__(log)
            res = Result.good(val)
        except E.WarpError as err:
            P.nprint(ICON_E, err, sep='\n') if log else None
            res = Result.bad(RuntimeError(f"internal error: {err}"))
        except BaseException as err:
            P.nprint(ICON_E, err, sep='') if log else None
            res = Result.bad(err)
        P.nprint(ICON_O, res, '\n') if log else None
        return res

    async def __execute_async__(self, log: bool) -> TermT:
        return self.__execute__(log)

    ############################################################################

    @abstractmethod
    def encode(self, codec: 'EncoderP') -> 'ReplRequestMsg': ...


################################################################################

class ReplInit(ReplRequest):

    __slots__ = __match_args__ = 'repl', 'globals', 'locals'

    globals: Rec[TermT]
    locals: Rec[TermT]

    def __init__(self, globals_: Rec[TermT], locals_: Rec[TermT]):
        self.globals = globals_
        self.locals = locals_

    def __execute__(self, log: bool):
        if log:
            P.nprint(ICON_I, f'ReplInit({len(self.globals)}.., {len(self.locals)}..)')

        ORDER_MARKER = '|'
        hidden_set: set[str] = set()

        def process_vars(dct: dict[str, object]) -> dict[str, object]:

            if '__hidden_names' in dct:
                hidden = dct.get('__hidden_names')
                if isinstance(hidden, (list, tuple, set)) and all(isinstance(x, str) for x in hidden):
                    hidden_set.update(hidden)
                    dct = {k: v for k, v in dct.items() if k != '__hidden_names'}

            if dct and any(ORDER_MARKER in k for k in dct.keys()):
                key_map: list[tuple[int, str, str]] = []
                for marked_name in dct.keys():
                    if ORDER_MARKER in marked_name:
                        name, idx = marked_name.split(ORDER_MARKER, 1)
                        try:
                            pos = int(idx)
                        except Exception:
                            pos = 0
                        key_map.append((pos, name, marked_name))
                    else:
                        key_map.append((10**9, marked_name, marked_name))

                ordered: dict[str, object] = {}
                for _, name, orig in sorted(key_map, key=lambda t: t[0]):
                    ordered[name] = dct[orig]
                return ordered

            return dct

        global_vars = process_vars(self.globals or {})
        local_vars = process_vars(self.locals or {})

        if log:
            for k, v in global_vars.items():
                P.nprint(ICON_M, f'will set global {k!r} =', f_object_id(v))

            for k, v in local_vars.items():
                P.nprint(ICON_M, f'will set local {k!r} =', f_object_id(v))

        return self.repl.initialize(
            local_vars=local_vars,
            global_vars=global_vars,
            hidden_vars=tuple(hidden_set),
        )

    def encode(self, enc):
        from ..msg.rpc_request_repl import ReplInitMsg
        return ReplInitMsg(
            enc.enc_raw(self.globals),
            enc.enc_raw(self.locals),
        )


################################################################################

# false positives are fine!

async_hints = (
    'await', 'async', 'asyncio', 'run', 'run_until_complete', 'gather',
    'get_event_loop', 'new_event_loop',
    'current_task', 'create_task', 'as_completed', 'wait', 'wait_for',
    'Future', 'Task', 'TaskGroup'
)

ASYNC_SOURCE_RE = re.compile(rf'\b({'|'.join(async_hints)})\b')

class ReplRunCode(ReplRequest):

    __slots__ = __match_args__ = 'repl', 'source', 'options',

    source:  str
    options: KwargsT

    def __init__(self, source: str, **options):
        self.source = source
        self.options = options

    @property
    def is_async(self) -> bool:
        # This used to check for do:
        #return bool(ASYNC_SOURCE_RE.match(self.source))
        # since false positives are completely fine.
        # For now, to avoid having to deal with different logic for each, simply return True.
        #return 'await ' in self.source or 'async ' in self.source
        return True

    def __execute__(self, log: bool) -> 'ReplEvaluationInfo':
        self.__log_input__(log)
        return self.repl.run_code_info(self.source, **self.options)

    async def __execute_async__(self, log: bool) -> TermT:
        self.__log_input__(log)
        info = await self.repl.async_run_code_info(self.source, **self.options)
        return info

    def __log_input__(self, log: bool):
        if not log:
            return
        f_source = self.source.strip('\n')
        f_source = FMT_CODE(f_source)
        if '\n' in f_source:
            P.nprint(ICON_I, f"'''\n{f_source}\n'''")
        else:
            P.nprint(ICON_I, f_source)

    def encode(self, enc):
        from ..msg.rpc_request_repl import ReplRunCodeMsg
        return ReplRunCodeMsg(self.source, self.options)


################################################################################

class ReplCallMethod(ReplRequest):

    __slots__ = __match_args__ = 'repl', 'method', 'pos', 'key'

    method: str
    pos:    ArgsT
    key:    KwargsT

    def __init__(self, method: str, pos: ArgsT, key: KwargsT):
        self.method = method
        self.pos = pos
        self.key = key

    def __execute__(self, log: bool):
        if log:
            P.nprint(ICON_I, f'repl.{self.method}(', *self.pos, ')')
        fn = getattr(self.repl, self.method)
        return fn(*self.pos, **self.key)

    def encode(self, enc):
        from ..msg.rpc_request_repl import ReplCallMethodMsg
        return ReplCallMethodMsg(self.method, enc.enc_args(self.pos), enc.enc_kwargs(self.key))


################################################################################

LOG_REPL = LogFlag('REPL')

color = P.MEDIUM.R
ICON_I = color @ '<<<'
ICON_Q = color @ '`'
ICON_M = color @ '---'
ICON_O = color @ '>>>'
ICON_E = color @ '!!!'
FMT_CODE = color
