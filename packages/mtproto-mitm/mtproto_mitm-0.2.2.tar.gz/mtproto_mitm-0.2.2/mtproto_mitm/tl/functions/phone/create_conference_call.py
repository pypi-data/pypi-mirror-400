from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7d0444bb, name="functions.phone.CreateConferenceCall")
class CreateConferenceCall(TLObject):
    flags: Int = TLField(is_flags=True)
    muted: bool = TLField(flag=1 << 0)
    video_stopped: bool = TLField(flag=1 << 2)
    join: bool = TLField(flag=1 << 3)
    random_id: Int = TLField()
    public_key: Optional[Int256] = TLField(flag=1 << 3)
    block: Optional[bytes] = TLField(flag=1 << 3)
    params: Optional[TLObject] = TLField(flag=1 << 3)
