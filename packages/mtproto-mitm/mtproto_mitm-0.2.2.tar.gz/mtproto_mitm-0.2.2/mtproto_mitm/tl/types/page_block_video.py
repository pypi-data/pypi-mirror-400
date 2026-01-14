from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7c8fe7b6, name="types.PageBlockVideo")
class PageBlockVideo(TLObject):
    flags: Int = TLField(is_flags=True)
    autoplay: bool = TLField(flag=1 << 0)
    loop: bool = TLField(flag=1 << 1)
    video_id: Long = TLField()
    caption: TLObject = TLField()
