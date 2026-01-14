# fmt: off

from agentica_internal.warpc.messages import *



def verify_pair(old: Msg, new: Msg):
    assert old.upgrade() == new, f"{old.upgrade()=}  !=  {new}"
    assert new.downgrade() == old, f"{new.downgrade()=}  !=  {old}"


def verify_legacy_conversion():
    request_data = ResourceHasAttrMsg(obj=UserResourceMsg(rid=(0, 1, 2)), attr='foo')
    response_data = ValueMsg(NumberMsg(v=True))

    old_request_msg = legacy.LegacyResourceRequestMsg(mid=3, fid=4, pid=4, info=request_data)
    new_request_msg = FramedRequestMsg(mid=3, fid=4, data=request_data)

    verify_pair(old_request_msg, new_request_msg)

    old_response_msg = legacy.LegacyResourceReplyMsg(mid=3, fid=4, pid=4, info=response_data)
    new_response_msg = FramedResponseMsg(mid=3, fid=4, data=response_data)

    verify_pair(old_response_msg, new_response_msg)

    old_mfi_msg = legacy.LegacyMFIReplyMsg.make(response_data)
    new_mfi_msg = FutureResultMsg(fid=-1, data=response_data)
    verify_pair(old_mfi_msg, new_mfi_msg)


if __name__ == '__main__':
    verify_legacy_conversion()
