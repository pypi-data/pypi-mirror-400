from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x598a92a, name="types.InputGroupCallStream")
class InputGroupCallStream(TLObject):
    flags: Int = TLField(is_flags=True)
    call: TLObject = TLField()
    time_ms: Long = TLField()
    scale: Int = TLField()
    video_channel: Optional[Int] = TLField(flag=1 << 0)
    video_quality: Optional[Int] = TLField(flag=1 << 0)
