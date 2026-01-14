from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xad613491, name="types.InputMediaUploadedThumbDocument_44")
class InputMediaUploadedThumbDocument_44(TLObject):
    file: TLObject = TLField()
    thumb: TLObject = TLField()
    mime_type: str = TLField()
    attributes: list[TLObject] = TLField()
    caption: str = TLField()
