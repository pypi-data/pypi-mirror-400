from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe13fd4bc, name="types.InputMediaUploadedVideo_28")
class InputMediaUploadedVideo_28(TLObject):
    file: TLObject = TLField()
    duration: Int = TLField()
    w: Int = TLField()
    h: Int = TLField()
    caption: str = TLField()
