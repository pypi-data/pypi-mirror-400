from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa76a5392, name="functions.stickers.SetStickerSetThumb")
class SetStickerSetThumb(TLObject):
    flags: Int = TLField(is_flags=True)
    stickerset: TLObject = TLField()
    thumb: Optional[TLObject] = TLField(flag=1 << 0)
    thumb_document_id: Optional[Long] = TLField(flag=1 << 1)
