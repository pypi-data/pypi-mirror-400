# fmt: off

import ast

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from types import FunctionType
from typing import NamedTuple, Any, NoReturn
from textwrap import dedent
from linecache import cache as LINECACHE

from ..core.hashing import raw_str_hash
from ..cpython.code import is_async_code

from .repl_alias import *
from .repl_cookie import Cookie, compile_with_cookies

__all__ = [
    'ReplCode',
    'CompileOpts',
    'RaiseFn',
    'ReturnFn',
]


################################################################################

type SyncFunction  = Callable[[], None]
type AsyncFunction = Callable[[], Coroutine[None, None, None]]

type RaiseFn   = Callable[[BaseException], BaseException]
type ReturnFn  = Callable[[Any], NoReturn]
type DisplayFn = Callable[[Any], None]
type ErrorCls  = type[BaseException]

################################################################################

@dataclass
class CompileOpts:
    """
    Stores the hook functions and other metadata that controls how source is
    compiled by `Repl.run_code`.
    """
    display_fn:     DisplayFn | None = None
    raise_fn:       RaiseFn | None = None
    return_fn:      ReturnFn | None = None
    return_var:     str | None = None
    allow_await:    bool = False
    run_is_await:   bool = False
    do_not_catch:    ErrorCls | tuple[ErrorCls, ...] = ()

    def needs_rewrite(self) -> bool:
        return self.return_fn or self.raise_fn or self.run_is_await or self.do_not_catch != ()

DEFAULTS = CompileOpts()


################################################################################

class ReplCode(NamedTuple):
    """
    The result of the compilation step used in `Repl.run_code`.

    This does some cool stuff: it injects the compiled source into `linecache`
    so that stack traces will 'find' the underlying 'files' (which do not
    exist on disk) that contain the source.
    """

    source:       str
    source_hash:  int
    function:     SyncFunction | AsyncFunction
    syntax_error: SyntaxError | None
    is_async:     bool

    @property
    def sync_function(self) -> SyncFunction:
        assert not self.is_async
        return self.function

    @property
    def async_function(self) -> AsyncFunction:
        assert self.is_async
        return self.function

    # implementation attached later...
    @staticmethod
    def from_source(*, source: str, scope: Vars, uid: str = '', opts: CompileOpts = DEFAULTS) -> 'ReplCode':
        ...

    def __del__(self) -> None:
        unregister_source(self.source_hash)

# ------------------------------------------------------------------------------

NEXT_ID = 0

def from_source(*, source: str, scope: Vars, uid: str = '', opts: CompileOpts = DEFAULTS) -> 'ReplCode':
    """
    Used by `repl.run_code` to compile source code into a `ReplCode` object,
    implementing special AST rewrites via `rewrite_ast` to incorporate the
    hook functions defined in `CompileOpts`.
    """

    uid = uid or repl_uid()
    file_name = f'/repl/{uid}'
    func_name = f'__repl_{uid}__'

    source = dedent(source)
    try:
        tree = ast.parse(source)
        tree = rewrite_ast(tree, opts)
        # print_tree(tree)

    except SyntaxError as syntax_error:
        return from_syntax_error(source, syntax_error)

    source_hash = repl_code_source_hash(source, opts)
    register_source(file_name, source_hash, source)

    flags = ALLOW_TOP_LEVEL_AWAIT if opts.allow_await else 0

    module_code = compile_with_cookies(tree, file_name, 'exec', flags=flags, cookies=opts)
    function = FunctionType(module_code, scope, func_name)

    source_hash = source_hash or repl_code_source_hash(source)
    is_async = is_async_code(function.__code__)

    return ReplCode(
        source=source,
        source_hash=source_hash,
        function=function,
        syntax_error=None,
        is_async=is_async,
    )

ReplCode.from_source = staticmethod(from_source)

NEXT_UID = 0

# ------------------------------------------------------------------------------

def repl_uid() -> int:
    global NEXT_UID
    NEXT_UID += 1
    return NEXT_UID

def repl_code_source_hash(source: str, opts: CompileOpts = DEFAULTS) -> int:
    str_hash = raw_str_hash(source)
    opt_hash = (1 if opts.display_fn else 0) | (2 if opts.allow_await else 0)
    return str_hash ^ opt_hash

ALLOW_TOP_LEVEL_AWAIT  = 0x2000

# ------------------------------------------------------------------------------

def from_syntax_error(source: str, syntax_error: SyntaxError) -> 'ReplCode':

    def raise_error():
        raise syntax_error

    return ReplCode(
        source=source,
        source_hash=0,
        function=raise_error,
        syntax_error=syntax_error,
        is_async=False
    )


# ------------------------------------------------------------------------------

def rewrite_ast(tree: ast.Module, opts: CompileOpts) -> ast.Module:
    """
    Rewrites the result of `ast.parse` to implement special functionality:

    * replaces `return XXX` with `result_fn(XXX)`
    * replaces `raise XXX` with `raise raise_fn(XXX)`
    * replaces `result_var = XXX` with `result_var = result_fn(XXX)`
    * replaces the last expression in `stmt; expr` with `stmt; display_fn(expr)`.
    """

    if not tree.body:
        return tree

    if opts.display_fn:
        last = tree.body[-1]
        if isinstance(last, ast.Expr):
            hooked = make_fn_node(last.value, Cookie.display_fn, wrap_expr=True)
            tree.body[-1] = hooked

    if opts.needs_rewrite():
        rewriter = ReturnRewriter()
        rewriter.rv_name = opts.return_var
        rewriter.rw_return = bool(opts.return_fn)
        rewriter.rw_raise = bool(opts.raise_fn)
        rewriter.rw_run = bool(opts.run_is_await)
        rewriter.rw_try = opts.do_not_catch != ()
        return rewriter.visit(tree)

    return tree

class ReturnRewriter(ast.NodeTransformer):

    rv_name:   str | None
    rw_return: bool
    rw_raise:  bool
    rw_run:    bool
    rw_try:    bool

    def visit_Return(self, node: ast.Return):
        if self.rw_return:
            if arg_node := node.value:
                return_arg = self.visit(arg_node)
            else:
                return_arg = ast.Constant(None)
            return make_fn_node(return_arg, Cookie.return_fn, wrap_expr=True)
        return node

    def visit_Raise(self, node: ast.Raise):
        if self.rw_raise and node.exc is not None:
            if exc_node := node.exc:
                exc_node = self.visit(exc_node)
            node.exc = make_fn_node(exc_node, Cookie.raise_fn)
        return node

    def visit_Try(self, node: ast.Try):
        if self.rw_try:
            reraise_node = ast.ExceptHandler(
                type=ast.Constant(Cookie.do_not_catch.value),
                body=[ast.Raise()]
            )
            node.handlers.insert(0, reraise_node)
            ast.fix_missing_locations(node)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        return node

    def visit_AsyncFunctionDef(self, node: ast.FunctionDef):
        return node

    def visit_Assign(self, node: ast.Assign):
        if not self.rv_name or not node.targets:
            return node
        lhs = node.targets[0]
        if isinstance(lhs, ast.Name) and lhs.id == self.rv_name:
            assign_node = ast.NamedExpr(target=lhs, value=node.value)
            return make_fn_node(assign_node, Cookie.return_fn, wrap_expr=True)
        else:
            return self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # not foolproof, but may be helpful to agent.
        if self.rw_run:
           match node.func:
               case ast.Attribute(value=ast.Name(id='asyncio'), attr='run'):
                   node = ast.Await(value=node.args[0])
                   ast.fix_missing_locations(node)
        return self.generic_visit(node)

def make_fn_node(arg_node, cookie: Cookie, wrap_expr: bool = False):
    class_node = ast.Constant(cookie.value)
    node = ast.Call(class_node, args=[arg_node], keywords=[])
    node = ast.Expr(node) if wrap_expr else node
    ast.fix_missing_locations(node)
    return node

# ------------------------------------------------------------------------------

def has_top_level_await(tree: ast.AST) -> bool:

    def check_node(node: ast.AST) -> bool:
        cls = type(node)
        if cls in LEAF_NODES:
            return False
        elif cls in ASYNC_NODES:
            return True
        else:
            return any(map(check_node, ast.iter_child_nodes(node)))

    return check_node(tree)

ASYNC_NODES = ast.Await, ast.AsyncWith, ast.AsyncFor
LEAF_NODES = ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.Name, ast.Constant

################################################################################

SOURCES: dict[int, str] = {}

def register_source(file_name: str, source_hash: int, source: str) -> None:
    def get_source() -> str | None:
        return SOURCES.get(source_hash)

    SOURCES[source_hash] = source
    LINECACHE[file_name] = get_source,

def unregister_source(source_hash: int):
    SOURCES.pop(source_hash, None)

################################################################################

def print_tree(tree: ast.AST) -> None:
    f_tree = ast.dump(tree, indent=3)
    print(f_tree)
