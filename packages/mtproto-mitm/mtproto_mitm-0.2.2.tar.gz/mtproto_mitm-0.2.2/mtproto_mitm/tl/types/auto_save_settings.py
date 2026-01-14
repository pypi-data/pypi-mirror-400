from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc84834ce, name="types.AutoSaveSettings")
class AutoSaveSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    photos: bool = TLField(flag=1 << 0)
    videos: bool = TLField(flag=1 << 1)
    video_max_size: Optional[Long] = TLField(flag=1 << 2)
