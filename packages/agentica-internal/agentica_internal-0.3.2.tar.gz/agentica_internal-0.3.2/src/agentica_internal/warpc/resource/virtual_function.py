# fmt: off

from .__ import *
from .base import *

__all__ = [
    'FunctionData',
]


################################################################################

WARP_OVERLOAD_MAGIC = hash('warp_overloads') << 32


def register_overload(func: FunctionT, overload_fn: FunctionT):
    """register a virtual warp overload if non-warp overloads not already present"""
    import typing
    from collections import defaultdict

    # {module: {qualname: {firstlineno: func}}}
    overloads: defaultdict[str, defaultdict[str, dict[int, FunctionT]]] | None
    overloads = getattr(typing, '_overload_registry', None) # type: ignore

    if overloads is not None:
        # register overload if not already overloads for this function
        f = getattr(func, '__func__', func)
        o_fn = getattr(overload_fn, '__func__', overload_fn)
        # overloads are distinguished by their line number.
        # to avoid any virtual overloads from clashing with the real overloads,
        # we OR the line number with a magic value.
        lineno = o_fn.__code__.co_firstlineno | WARP_OVERLOAD_MAGIC
        linenos = overloads[f.__module__][f.__qualname__].keys()
        if all(_is_warp_overload(l) for l in linenos):
            overloads[f.__module__][f.__qualname__][lineno] = overload_fn


def retrieve_overloads(func: FunctionT) -> tuple[FunctionT, ...]:
    """retrieve genuine non-warp overloads for a function"""
    import typing
    from collections import defaultdict

    # {module: {qualname: {firstlineno: func}}}
    overloads: defaultdict[str, defaultdict[str, dict[int, FunctionT]]] | None
    overloads = getattr(typing, '_overload_registry', None) # type: ignore

    if overloads is None:
        return ()

    f = getattr(func, '__func__', func)
    if f.__module__ not in overloads:
        return ()
    mod_dict = overloads[f.__module__]
    if f.__qualname__ not in mod_dict:
        return ()

    matches = mod_dict[f.__qualname__].items()
    return tuple(o for l, o in matches if not _is_warp_overload(l))


def _is_warp_overload(lineno: int) -> bool:
    return lineno & WARP_OVERLOAD_MAGIC == WARP_OVERLOAD_MAGIC

################################################################################

class FunctionData(ResourceData):
    __slots__ = (
        'name', 'qname', 'module', 'lineno', 'doc', 'keys', 'annos', 'defaults',
        'args', 'pos_args', 'key_args', 'opt_args', 'pos_star', 'key_star',
        'sig', 'owner', 'overloads', 'is_async', 'async_mode'
    )

    FORBIDDEN_FORM = forbidden_function

    name:      str
    qname:     optstr
    module:    optstr
    lineno:    int
    doc:       optstr
    keys:      strtup
    annos:     AnnotationsT
    defaults:  AttributesT

    args:      strtup
    pos_args:  strtup
    key_args:  strtup
    opt_args:  strtup
    pos_star:  optstr
    key_star:  optstr

    sig:       object | None
    owner:     type | None
    overloads: Tup['FunctionData']

    is_async:   bool
    async_mode: AsyncMode

    # implementation attached later
    @classmethod
    def describe_resource(cls, fun: FunctionT, is_overload: bool = False) -> 'FunctionData': ...

    # implementation attached later
    def create_resource(self, handle: ResourceHandle) -> FunctionT: ...


################################################################################

def describe_real_function(function: FunctionT,
                           is_overload: bool = False,
                           process_defaults: bool = True) -> FunctionData:
    from agentica_internal.cpython.function import func_sig_info
    from agentica_internal.cpython.inspect import (callable_module_and_name,
                                               has_coroutine_mark,
                                               resolve_callable)

    data = FunctionData()

    fun, skip = resolve_callable(function)

    info = func_sig_info(fun)
    pos_args, add_pos = mklist()
    reg_args, add_reg = mklist()
    key_args, add_key = mklist()
    opt_args, add_opt = mklist()
    for arg in info.arg_info[skip:]:
        name = arg.name
        if arg.pos_only:
            add_pos(name)
        elif arg.key_only:
            add_key(name)
        else:
            add_reg(name)
        if arg.optional:
            add_opt(name)

    data.args = tuple(reg_args)
    data.pos_args = tuple(pos_args)
    data.key_args = tuple(key_args)
    data.opt_args = tuple(opt_args)

    data.pos_star = info.pos_star
    data.key_star = info.key_star
    data.is_async = is_async = info.is_async | has_coroutine_mark(fun)
    data.owner    = None
    # for now, this will be set later during FunctionData.encode_fields, where the owning class
    # is known via `.enc_owner()`.

    async_mode = flags.DEFAULT_ASYNC_MODE if is_async else None

    mname, qname, name = callable_module_and_name(fun)
    if mname == '__main__':
        mname = None
    if qname == name:
        qname = None

    data.module, data.qname, data.name = mname, qname, name

    if is_forbidden(function, mname):
        raise E.WarpEncodingForbiddenError(f"<function '{mname}.{qname}'>")

    data.lineno = 0
    if co := getattr(fun, '__code__', None):
        data.lineno = co.co_firstlineno

    fdict, doc, annos = multi_get_raw(fun, DICT, DOC, ANNOS)
    data.keys = tuple(fdict.keys()) if is_rec(fdict) else ()
    data.doc = doc if is_optstr(doc) else None
    data.annos = annos if is_rec(annos) else {}

    defaults_flag: Any = flags.VIRTUAL_FUNCTION_DEFAULTS if process_defaults else 'all'
    data.defaults = get_fun_defaults(fun, data.opt_args, defaults_flag)
    data.sig = getattr(fun, '__signature__', None)
    data.async_mode = async_mode
    if is_overload:
        data.overloads = ()
    else:
        data.overloads = tuple(describe_real_function(o, is_overload=True) for o in retrieve_overloads(fun))

    return data


################################################################################

def get_fun_defaults(fun: FunctionT, opt_args: strtup, flag: Literal['all', 'atoms', None]) -> dict[str, Any]:
    if not opt_args or flag is None:
        return {}
    defaults = getattr(fun, '__defaults__', None)
    if not defaults or type(defaults) is not tuple:
        return {}
    if flag == 'atoms':
        return {
            k: v for k, v in zip(opt_args, defaults)
            if is_atom_t(v) or is_class_t(v) or is_function_t(v)
        }
    else:
        return dict(zip(opt_args, defaults))


################################################################################

def create_virtual_function(data: FunctionData, handle: ResourceHandle) -> FunctionT:

    name, qname = data.name, data.qname
    qname = qname or name
    lineno = data.lineno
    annos = data.annos
    arg_defaults = data.defaults

    handle.name = name
    handle.kind = Kind.Function
    handle.keys = list(data.keys)
    handle.open = False

    is_async = data.is_async
    async_mode = data.async_mode

    if async_mode not in ('sync', None):
        assert is_async

    if is_async and async_mode == 'sync':
        async_mode = 'coro'

    if is_async and async_mode is None:
        async_mode = flags.DEFAULT_ASYNC_MODE

    if async_mode == 'future':
        import asyncio
        if 'return' in annos:
            annos['return'] = asyncio.Future[annos['return']]
        else:
            # https://peps.python.org/pep-0484/#the-meaning-of-annotations
            annos['return'] = asyncio.Future[Any]

    meta = {
        VHDL: handle,
        NAME: name,
        QUALNAME: qname,
        MODULE: data.module,
        DOC: data.doc,
        ANNOS: annos,
    }

    prm_str, pos_str, key_str = make_template_strs(data)

    modifiers = ''
    if async_mode == 'future':
        modifiers += ".set_async_mode('future')"
    elif async_mode == 'coro':
        modifiers += ".set_async_mode('coro')"

    result = f'''return {VHDL_ARG}.hdlr({VHDL_ARG}, {CALL_ARG}({INNER}, {pos_str}, {key_str}){modifiers})'''

    # this prevents us from virtualizing 'init', which has already happened because we
    # called '__new__' via RPC
    if qname.endswith('.__init__'):
        result = 'pass'

    code = f'''
def {MAKER}({VHDL_ARG}, {CALL_ARG}, {ARG_DEFAULTS}, {BLANK_DEFAULT}):
    def {INNER}{prm_str}:
        {result}
    return {INNER}'''

    try:
        exec(code, ns := {})
    except BaseException as err:
        fst = code.strip().splitlines()[1].strip()
        raise E.WarpDecodingError(
            f'function stub error!\n{handle=!r}\nsig={fst!r}\n{data=!r}\n{err=!r}\n\n{code}'
        )

    v_fun_maker = ns[MAKER]
    v_fun = v_fun_maker(handle, ResourceCallFunction, arg_defaults, ARG_DEFAULT)
    assert isinstance(v_fun, FunctionType)
    multi_set_raw(v_fun, meta)
    v_fun.__code__ = v_fun.__code__.replace(co_name=name, co_qualname=qname, co_firstlineno=lineno)

    if sig := data.sig:
        v_fun.__signature__ = sig

    if async_mode == 'coro':
        from inspect import markcoroutinefunction
        markcoroutinefunction(v_fun)

    for overload in data.overloads:
        overload_fn = create_overload_dummy_function(overload)
        register_overload(v_fun, overload_fn)

    return v_fun

################################################################################

def create_proxy_function(data: FunctionData, impl_fn: Callable) -> FunctionType:

    name = data.name
    qname = data.qname or name
    lineno = data.lineno
    prm_str, pos_str, key_str = make_template_strs(data)

    fwd_str = combine_pos_key_str(pos_str, key_str)
    result = f'''return {IMPL_FN_ARG}({fwd_str})'''

    arg_defaults = data.defaults if data.defaults else {}
    code = f'''
def {P_MAKER}({IMPL_FN_ARG}, {ARG_DEFAULTS}, {BLANK_DEFAULT}):
    def {P_INNER}{prm_str}:
        {result}
    return {P_INNER}'''

    exec(code, ns := {})

    p_fun_maker = ns[P_MAKER]
    p_fun = p_fun_maker(impl_fn, arg_defaults, ARG_DEFAULT)
    assert isinstance(p_fun, FunctionType)
    p_fun.__name__ = name
    p_fun.__qualname__ = qname
    p_fun.__module__ = data.module
    p_fun.__code__ = p_fun.__code__.replace(co_name=name, co_qualname=qname, co_firstlineno=lineno)
    p_fun.__doc__ = data.doc
    p_fun.__annotations__ = data.annos
    # TODO: set __text_signature__ to something helpful here...

    if sig := data.sig:
        p_fun.__signature__ = sig

    if data.is_async:
        from inspect import markcoroutinefunction
        markcoroutinefunction(p_fun)

    for overload in data.overloads:
        overload_fn = create_overload_dummy_function(overload)
        register_overload(p_fun, overload_fn)

    return p_fun

################################################################################

def _overload_dummy(*args, **kwds):
    """Helper for @overload to raise when called."""
    del args  # for vulture
    del kwds
    raise NotImplementedError(
        "You should not call an overloaded function. "
        "A series of @overload-decorated functions "
        "outside a stub module should always be followed "
        "by an implementation that is not @overload-ed.")

def create_overload_dummy_function(data: FunctionData) -> FunctionType:
    import typing
    dummy = getattr(typing, '_overload_dummy', None)
    if dummy is None:
        dummy = _overload_dummy
    o_fun = create_proxy_function(data, dummy)
    return o_fun

################################################################################

# these have to be not clash with func arg names, so we use constants to make the above code more
# readable

ARG_DEFAULTS = '___ARG_DEFAULTS___'
BLANK_DEFAULT = '___BLANK_DEFAULT___'

MAKER = '___MAKE_VIRTUAL_FN___'
INNER = '___VIRTUAL_FN___'

P_MAKER = '___MAKE_PROXY_FN___'
P_INNER = '___PROXY_FN___'

V_CALLBACK_ARG = '___VCALLBACK_ARG___'
GRID_ARG = '___GRID_ARG___'
CALL_ARG = '___CALL_ARG___'
HANDLER_ARG = '___HANDLER_ARG___'
VHDL_ARG = '___VHDL_ARG___'
IMPL_FN_ARG = '___IMPL_FN_ARG___'

################################################################################

def make_template_strs(data: FunctionData) -> tuple[str, str, str]:
    """
    This function returns a triple (prm_str, pos_str, key_str):

    1) param_str: a string like '(arg1, /, *args, **kwargs)', specifying the function
    arguments as they should appear in the `def NAME{prm_str}`.

    2) pos_str: a string like '(arg1, *args)', specifying the positional arguments
    as they should be forwarded as a tuple.

    3) key_str: a string like '{key1=val1, **kwargs}', specifying the keyword
    arguments as thy should be forwarded as a dictionary.

    You can build the 'combined' arguments as they should be forwarded to the
    *true* implementation via `combine_pos_key_str(pos_str, key_str)`.
    """
    reg_args = data.args
    pos_args = data.pos_args
    key_args = data.key_args
    pos_star = data.pos_star
    key_star = data.key_star
    opt_args = data.opt_args
    arg_defs = data.defaults

    prm_strs, add_prm = mklist()
    pos_strs, add_pos = mklist()
    key_strs, add_key = mklist()

    def add_arg(name: str):
        if name in opt_args:
            if name in arg_defs:
                add_prm(f'{name}={ARG_DEFAULTS}[{name!r}]')
            else:
                add_prm(f'{name}={BLANK_DEFAULT}')
        else:
            add_prm(name)

    if pos_args:
        for arg in pos_args:
            add_arg(arg)
            add_pos(arg)
        add_prm('/')

    for arg in reg_args:
        add_arg(arg)
        if arg in opt_args:
            add_key(f'{arg!r}:{arg}')
        else:
            add_pos(arg)

    if pos_star:
        add_arg('*' + pos_star)

    if key_args:
        if not pos_star:
            add_prm('*')
        for arg in key_args:
            add_arg(arg)
            add_key(f'{arg!r}:{arg}')

    if key_star:
        add_arg('**' + key_star)

    if len(pos_strs) == 1:
        pos_strs.append('')

    prm_str = '(' + commas(prm_strs) + ')'
    pos_str = '(' + commas(pos_strs) + ')'
    key_str = '{' + commas(key_strs) + '}'

    if key_star:
        if key_str == '{}':
            key_str = key_star
        else:
            key_str = key_str[1:-1].removesuffix(', ')
            key_str = f'{{{key_str}, **{key_star}}}'

    if pos_star:
        if pos_str == '()':
            pos_str = pos_star
        else:
            pos_str = pos_str[1:-1].removesuffix(', ')
            pos_str = f'({pos_str}, *{pos_star})'

    return prm_str, pos_str, key_str


commas = ', '.join

################################################################################

def combine_pos_key_str(pos_str, key_str):
    if pos_str.startswith('(') and pos_str.endswith(')'):
        pos_str = pos_str[1:-1].rstrip(', ')
    else:
        # if pos_str is just 'args'
        pos_str = f'*{pos_str}'

    if key_str:
        key_str = f'**{key_str}'

    if not pos_str and not key_str:
        return ''
    if not pos_str:
        return key_str
    if not key_str:
        return pos_str
    return f'{pos_str}, {key_str}'

################################################################################

# attach definitions to class
FunctionData.describe_resource = staticmethod(describe_real_function)
FunctionData.create_resource = create_virtual_function
