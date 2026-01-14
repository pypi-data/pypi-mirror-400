from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1759c560, name="types.PageBlockPhoto")
class PageBlockPhoto(TLObject):
    flags: Int = TLField(is_flags=True)
    photo_id: Long = TLField()
    caption: TLObject = TLField()
    url: Optional[str] = TLField(flag=1 << 0)
    webpage_id: Optional[Long] = TLField(flag=1 << 0)
