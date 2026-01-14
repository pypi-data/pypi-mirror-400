from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x524a415d, name="types.DecryptedMessageMediaVideo_15")
class DecryptedMessageMediaVideo_15(TLObject):
    thumb: bytes = TLField()
    thumb_w: Int = TLField()
    thumb_h: Int = TLField()
    duration: Int = TLField()
    mime_type: str = TLField()
    w: Int = TLField()
    h: Int = TLField()
    size: Int = TLField()
    key: bytes = TLField()
    iv: bytes = TLField()
