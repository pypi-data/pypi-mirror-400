from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x43c57c48, name="types.DocumentAttributeVideo")
class DocumentAttributeVideo(TLObject):
    flags: Int = TLField(is_flags=True)
    round_message: bool = TLField(flag=1 << 0)
    supports_streaming: bool = TLField(flag=1 << 1)
    nosound: bool = TLField(flag=1 << 3)
    duration: float = TLField()
    w: Int = TLField()
    h: Int = TLField()
    preload_prefix_size: Optional[Int] = TLField(flag=1 << 2)
    video_start_ts: Optional[float] = TLField(flag=1 << 4)
    video_codec: Optional[str] = TLField(flag=1 << 5)
