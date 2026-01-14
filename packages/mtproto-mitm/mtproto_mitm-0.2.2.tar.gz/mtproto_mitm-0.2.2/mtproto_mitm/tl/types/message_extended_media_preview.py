from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xad628cc8, name="types.MessageExtendedMediaPreview")
class MessageExtendedMediaPreview(TLObject):
    flags: Int = TLField(is_flags=True)
    w: Optional[Int] = TLField(flag=1 << 0)
    h: Optional[Int] = TLField(flag=1 << 0)
    thumb: Optional[TLObject] = TLField(flag=1 << 1)
    video_duration: Optional[Int] = TLField(flag=1 << 2)
