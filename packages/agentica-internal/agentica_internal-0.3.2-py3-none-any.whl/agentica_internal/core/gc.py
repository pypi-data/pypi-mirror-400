import gc
import logging
import sys
from typing import Any

__all__ = [
    'log_refcount',
    'inspect_referrers',
    'print_newly_open_files',
]

logger = logging.getLogger(__name__)

_sentinel = object()


def log_refcount(obj: object, label: str, uid: Any = _sentinel) -> int:
    """Log the reference count of an object for debugging.

    Args:
        obj: the object to check
        label: description label (e.g., "before cleanup", "after cleanup")
        uid: a unique id for logging context, defaults to the object's hex ID

    Returns:
        The reference count (excluding the call to getrefcount itself)
    """
    if uid is _sentinel:
        uid = hex(id(obj))
    refcount = sys.getrefcount(obj) - 1  # -1 for the getrefcount call itself
    logger.debug(f"object {uid!r} refcount {label}: {refcount}")
    return refcount


def inspect_referrers(
    obj: object,
    comparison_dicts: dict[str, object] | None = None,
    uid: Any = _sentinel,
) -> None:
    """Inspect and log what objects are holding references to the given object.

    Args:
        obj: the object to inspect
        comparison_dicts: optional dict of name->dict pairs to identify specific dicts
        uid: a unique id for logging context, defaults to the object's hex ID
    """
    if uid is _sentinel:
        uid = hex(id(obj))
    refcount = sys.getrefcount(obj) - 1
    if refcount > 1:  # 1 is our local reference
        logger.debug(f"object {uid!r} still has {refcount} references, inspecting referrers...")
        referrers = gc.get_referrers(obj)
        for i, referrer in enumerate(referrers):
            if referrer is locals():
                continue  # Skip our own local namespace
            try:
                referrer_type = type(referrer).__name__
                if isinstance(referrer, dict) and comparison_dicts:
                    # Try to identify which dict it is
                    referrer_id = id(referrer)
                    identified = False
                    for name, comp_dict in comparison_dicts.items():
                        if referrer_id == id(comp_dict):
                            logger.debug(f"  Referrer {i}: {name} dict")
                            identified = True
                            break
                    if not identified:
                        logger.debug(f"  Referrer {i}: dict with {len(referrer)} items")
                elif referrer_type == "coroutine":
                    # Try to get coroutine name
                    try:
                        coro_name = referrer.__name__
                        coro_qualname = getattr(referrer, '__qualname__', '?')
                        logger.debug(
                            f"  Referrer {i}: coroutine '{coro_qualname}' (running={referrer.cr_running})"
                        )
                    except:
                        logger.debug(f"  Referrer {i}: {referrer_type}")
                elif referrer_type == "method":
                    # Try to get method name
                    try:
                        method_name = referrer.__name__
                        method_self = referrer.__self__
                        method_class = type(method_self).__name__
                        # Check if it's the same object (circular ref)
                        is_circular = method_self is obj
                        logger.debug(
                            f"  Referrer {i}: method '{method_class}.{method_name}' "
                            f"{'(circular ref)' if is_circular else ''}"
                        )
                    except:
                        logger.debug(f"  Referrer {i}: {referrer_type}")
                else:
                    logger.debug(f"  Referrer {i}: {referrer_type}")
            except Exception as e:
                logger.debug(f"  Referrer {i}: <unable to inspect: {e}>")


last_open: dict[int, set] = {}


def print_newly_open_files(pid: int | None = None) -> None:
    import psutil

    try:
        proc = psutil.Process(pid=pid)
        pid = proc.pid
        files = proc.open_files()
        for child in proc.children(recursive=True):
            try:
                files.extend(child.open_files())
            except:
                pass
    except:
        return

    this = set(files)

    if pid in last_open:
        last = last_open[pid]
    else:
        last_open[pid] = last = set()

    if not this and not last:
        return

    if not last:
        last.update(files)
    elif new := last - this:
        from ..core.print import tprint

        last.clear()
        last.update(this)
        f_files = '\n * '.join(f'{f.fd: 3}: {f.path!r}' for f in new)
        tprint(f'{len(new)} new open file:\n{f_files}', truncate=False, err=True)


def print_open_files(pid: int | None) -> None:
    from sys import __stderr__

    import psutil

    proc = psutil.Process(pid=pid)
    files = proc.open_files()
    f_files = '\n * '.join(f'{f.fd: 3}: {f.path!r}' for f in files)
    __stderr__.write(f_files + '\n')
    __stderr__.flush()
