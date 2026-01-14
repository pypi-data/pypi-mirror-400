from agentica_internal.cpython.ids import (
    SYS_CLASS_ID_DICT,
    SYS_FUNCTION_ID_DICT,
    SYS_OBJECT_ID_DICT,
)
from agentica_internal.warpc.system import (
    CLS_OFFSET,
    FUN_OFFSET,
    OBJ_OFFSET,
    SRID_TO_CLS,
    SRID_TO_FUN,
    SRID_TO_OBJ,
)


def verify_system_class_ids():
    for cls_name, cls_id in SYS_CLASS_ID_DICT.items():
        srid = cls_id + CLS_OFFSET
        assert srid in SRID_TO_CLS, f"system class {cls_name} not registered"


def verify_system_function_ids():
    for fun_name, fun_id in SYS_FUNCTION_ID_DICT.items():
        srid = fun_id + FUN_OFFSET
        assert srid in SRID_TO_FUN, f"system function {fun_name} not registered"


RENAMED = {'IN__is_coroutine_mark'}


def verify_system_object_ids():
    for obj_name, obj_id in SYS_OBJECT_ID_DICT.items():
        srid = obj_id + OBJ_OFFSET
        if obj_name in RENAMED:
            continue
        assert srid in SRID_TO_OBJ, f"system object {obj_name} not registered"


def verify_system_tables_disjoint():
    funs = set(map(id, SRID_TO_FUN.values()))
    clss = set(map(id, SRID_TO_CLS.values()))
    objs = set(map(id, SRID_TO_OBJ.values()))
    assert funs.isdisjoint(clss), f"classes and funtions not disjoint"
    assert objs.isdisjoint(clss), f"classes and objects not disjoint"
    assert funs.isdisjoint(objs), f"functions and objects not disjoint"


if __name__ == '__main__':
    verify_system_class_ids()
    verify_system_function_ids()
    verify_system_object_ids()
    verify_system_tables_disjoint()
