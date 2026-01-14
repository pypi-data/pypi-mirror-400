from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xffe76b78, name="types.InputMediaUploadedDocument_22")
class InputMediaUploadedDocument_22(TLObject):
    file: TLObject = TLField()
    mime_type: str = TLField()
    attributes: list[TLObject] = TLField()
