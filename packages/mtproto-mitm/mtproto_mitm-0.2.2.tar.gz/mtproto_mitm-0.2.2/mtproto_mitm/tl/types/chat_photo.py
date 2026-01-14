from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1c6e1c11, name="types.ChatPhoto")
class ChatPhoto(TLObject):
    flags: Int = TLField(is_flags=True)
    has_video: bool = TLField(flag=1 << 0)
    photo_id: Long = TLField()
    stripped_thumb: Optional[bytes] = TLField(flag=1 << 1)
    dc_id: Int = TLField()
