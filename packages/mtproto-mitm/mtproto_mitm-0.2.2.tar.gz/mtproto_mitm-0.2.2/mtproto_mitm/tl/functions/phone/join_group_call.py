from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8fb53057, name="functions.phone.JoinGroupCall")
class JoinGroupCall(TLObject):
    flags: Int = TLField(is_flags=True)
    muted: bool = TLField(flag=1 << 0)
    video_stopped: bool = TLField(flag=1 << 2)
    call: TLObject = TLField()
    join_as: TLObject = TLField()
    invite_hash: Optional[str] = TLField(flag=1 << 1)
    public_key: Optional[Int256] = TLField(flag=1 << 3)
    block: Optional[bytes] = TLField(flag=1 << 3)
    params: TLObject = TLField()
