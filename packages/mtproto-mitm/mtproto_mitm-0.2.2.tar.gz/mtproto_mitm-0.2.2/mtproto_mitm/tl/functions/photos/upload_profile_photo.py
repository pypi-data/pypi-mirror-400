from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x388a3b5, name="functions.photos.UploadProfilePhoto")
class UploadProfilePhoto(TLObject):
    flags: Int = TLField(is_flags=True)
    fallback: bool = TLField(flag=1 << 3)
    bot: Optional[TLObject] = TLField(flag=1 << 5)
    file: Optional[TLObject] = TLField(flag=1 << 0)
    video: Optional[TLObject] = TLField(flag=1 << 1)
    video_start_ts: Optional[float] = TLField(flag=1 << 2)
    video_emoji_markup: Optional[TLObject] = TLField(flag=1 << 4)
