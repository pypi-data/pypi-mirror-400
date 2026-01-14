from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe831c556, name="types.VideoSize_116")
class VideoSize_116(TLObject):
    flags: Int = TLField(is_flags=True)
    type_: str = TLField()
    location: TLObject = TLField()
    w: Int = TLField()
    h: Int = TLField()
    size: Int = TLField()
    video_start_ts: Optional[float] = TLField(flag=1 << 0)
