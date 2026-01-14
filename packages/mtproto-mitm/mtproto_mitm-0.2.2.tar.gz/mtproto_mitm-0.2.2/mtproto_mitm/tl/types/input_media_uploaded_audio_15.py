from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4e498cab, name="types.InputMediaUploadedAudio_15")
class InputMediaUploadedAudio_15(TLObject):
    file: TLObject = TLField()
    duration: Int = TLField()
    mime_type: str = TLField()
