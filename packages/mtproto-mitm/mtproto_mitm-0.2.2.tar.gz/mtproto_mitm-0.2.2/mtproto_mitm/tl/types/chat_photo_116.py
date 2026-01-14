from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd20b9f3c, name="types.ChatPhoto_116")
class ChatPhoto_116(TLObject):
    flags: Int = TLField(is_flags=True)
    has_video: bool = TLField(flag=1 << 0)
    photo_small: TLObject = TLField()
    photo_big: TLObject = TLField()
    dc_id: Int = TLField()
