# fmt: off

from ...core.strs import idsafe_str

from msgspec import msgpack
from re import compile as re_compile
from json import dumps as json_dumps


__all__ = [
    'dec_msgpack',
    'enc_msgpack',
    'fmt_msgpack',
    'pprint_msgpack'
]


################################################################################

dec_msgpack = msgpack.Decoder().decode
enc_msgpack = msgpack.Encoder().encode

################################################################################

def fmt_msgpack(msg: bytes, *, censor_ids: bool = False, multiline: bool = False) -> str:
    try:
        d = dec_msgpack(msg)
    except:
        return '<corrupt msgpack bytes>'
    s = json_dumps(d, indent='\t' if multiline else None, default=_to_json)
    if not multiline:
        s = SL_MID.sub(_fmt_mid, s)
        s = SL_RID.sub(_fmt_rid, s)
    if censor_ids:
        s = idsafe_str(s)
    if multiline:
        s = ML_RID.sub(r'[\1, \2, \3]', s)
    return s

def _to_json(obj):
    if isinstance(obj, bytes):
        return 'bytes:' + repr(obj)
    return '???'

def _fmt_mid(m):
    mid = int(m[1])
    return f'"mid": 0x{mid:x}'

def _fmt_rid(m):
    wid = int(m[1])
    fid = int(m[2])
    rid = int(m[3])
    return f'"rid": [0x{wid:x}, 0x{fid:x}, 0x{rid:x}]]'

################################################################################

def pprint_msgpack(msg: bytes, err: bool = False) -> None:
    from ...core.print import pprint
    data = dec_msgpack(msg)
    pprint(data, err=err)

SL_MID = re_compile(r'"mid": (\d+)')
SL_RID = re_compile(r'"rid": \[(\d+), (\d+), (\d+)]')
ML_RID = re_compile(r'\[\n\s+(\d+),\s+(\d+),\s+([0-9A-Fa-fx]+)\s+]')
