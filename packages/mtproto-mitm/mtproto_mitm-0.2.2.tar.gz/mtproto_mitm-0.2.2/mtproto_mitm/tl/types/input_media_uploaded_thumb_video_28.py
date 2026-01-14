from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x96fb97dc, name="types.InputMediaUploadedThumbVideo_28")
class InputMediaUploadedThumbVideo_28(TLObject):
    file: TLObject = TLField()
    thumb: TLObject = TLField()
    duration: Int = TLField()
    w: Int = TLField()
    h: Int = TLField()
    caption: str = TLField()
