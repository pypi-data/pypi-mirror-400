from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe14c4a71, name="functions.photos.UploadContactProfilePhoto")
class UploadContactProfilePhoto(TLObject):
    flags: Int = TLField(is_flags=True)
    suggest: bool = TLField(flag=1 << 3)
    save: bool = TLField(flag=1 << 4)
    user_id: TLObject = TLField()
    file: Optional[TLObject] = TLField(flag=1 << 0)
    video: Optional[TLObject] = TLField(flag=1 << 1)
    video_start_ts: Optional[float] = TLField(flag=1 << 2)
    video_emoji_markup: Optional[TLObject] = TLField(flag=1 << 5)
