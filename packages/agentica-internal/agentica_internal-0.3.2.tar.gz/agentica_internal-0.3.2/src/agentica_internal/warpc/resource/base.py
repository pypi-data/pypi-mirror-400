# fmt: off

from .__ import *
from .handle import ResourceHandle, get_handle

__all__ = [
    'ResourceData',
    'ResourceHandle',
    'get_handle',
]

################################################################################

#
# SNIPPETS = {
#     'ClassMsg':           'enc.enc_cls(data.{K})            data.{K} = dec.dec_cls(self.{K})',
#     'FunctionMsg':        'enc.enc_fun(data.{K})            data.{K} = dec.dec_fun(self.{K})',
#     'ValueT':             'enc.enc_val(data.{K})            data.{K} = dec.dec_val(self.{K})',
#     'MethodsMsg': 'mapdict(enc.enc_fun, data.{K})   data.{K} = mapdict(dec.dec_fun, '
#                           'self.{K})',
#     Rec[ResourceT]: 'mapdict(enc.enc_res, data.{K})   data.{K} = mapdict(dec.dec_fun, self.{K})',
#     AnnotationsT:   'enc.enc_ann(data.{K})            data.{K} = dec.dec_ann(self.{K})',
#
# }
#
#     'Tup[ClassT]': CLS_TUP = 1
#     'Tup[ClassT]': FUN_REC = 2
#     'Tup[ClassT]': TYP_REC
#     'Tup[ClassT]': VAL_REC
#     'Tup[ClassT]': SEQ
#     'Tup[ClassT]': VAL
#     'Tup[ClassT]': TYP_REC
#     'Tup[ClassT]': VAL_OR_NONE
#     'Tup[ClassT]': RES_REC
#     'Tup[ClassT]': SEQ_OR_VAL
#
# def compile_data_to_msg_encoder(attr: str, anno):
#     if cls(anno) is ForwardRef:
#
#

################################################################################

class ResourceData:
    __slots__ = ()

    STR_NAME: ClassVar[str]
    FORBIDDEN_FORM: ClassVar[ResourceT] = forbidden_object
    MSG_CLS: ClassVar['type[ResourceDataMsg]']
    MIGHT_ALIAS: ClassVar[bool] = False

    def encode(self, enc: EncoderP) -> 'ResourceDataMsg':
        cls = type(self)
        msg_cls = cls.MSG_CLS
        kwargs = msg_cls.encode_fields(self, enc)
        for key in msg_cls.__struct_fields__:
            if key not in kwargs:
                kwargs[key] = getattr(self, key)
        msg = msg_cls(**kwargs)
        return msg

    def repr(self):
        cls = type(self)
        if hasattr(cls, '__slots__'):
            dct = {}
            for slot in cls.__slots__:
                dct[slot] = getattr(self, slot, FIELD_ABSENT)
        else:
            dct = self.__dict__
        f_args = ', '.join(f'{k}={f_slot(k, v)}' for k, v in dct.items())
        return f'{cls.__name__}({f_args})'

    __str__ = repr
    __repr__ = repr

    def short_str(self) -> str:
        cls_name = type(self).__name__
        name = getattr(self, 'name', '...')
        return f'{cls_name}({name})'

    def pprint(self, err: bool = False):
        from ...core.fmt import f_slot_obj
        P.rprint(f_slot_obj(self), err=err)

    @classmethod
    def describe_resource(cls, resource: ResourceT, /) -> 'ResourceData': ...

    def create_resource(self, handle: 'ResourceHandle', /) -> ResourceT: ...

    @classmethod
    def forbidden_msg(cls) -> 'SystemResourceMsg':
        from ..msg.term_resource import SystemResourceMsg
        from ..system import LRID_TO_SRID
        forb_cls = cls.FORBIDDEN_FORM
        forb_sid = LRID_TO_SRID[id(forb_cls)]
        return SystemResourceMsg(forb_sid)

    def rename(self, tmpl: str | None, grid: GlobalRID) -> None:
        if tmpl and hasattr(self, 'name'):
            f_kind = type(self).__name__.removesuffix('Data')
            wid, fid, lid = grid
            name = tmpl.format(rsrc_name=self.name, rsrc_kind=f_kind, wid=wid, fid=fid, lid=lid)
            setattr(self, 'name', name)
            if type(getattr(self, 'qname', None)) is str:
                setattr(self, 'qname', name)
