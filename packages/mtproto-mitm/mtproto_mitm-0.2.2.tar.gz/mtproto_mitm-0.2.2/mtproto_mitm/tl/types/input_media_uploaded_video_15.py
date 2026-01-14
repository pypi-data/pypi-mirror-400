from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x133ad6f6, name="types.InputMediaUploadedVideo_15")
class InputMediaUploadedVideo_15(TLObject):
    file: TLObject = TLField()
    duration: Int = TLField()
    w: Int = TLField()
    h: Int = TLField()
    mime_type: str = TLField()
