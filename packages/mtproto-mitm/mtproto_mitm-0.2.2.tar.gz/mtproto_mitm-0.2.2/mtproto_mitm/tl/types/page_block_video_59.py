from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd9d71866, name="types.PageBlockVideo_59")
class PageBlockVideo_59(TLObject):
    flags: Int = TLField(is_flags=True)
    autoplay: bool = TLField(flag=1 << 1)
    loop: bool = TLField(flag=1 << 2)
    video_id: Long = TLField()
    caption: TLObject = TLField()
