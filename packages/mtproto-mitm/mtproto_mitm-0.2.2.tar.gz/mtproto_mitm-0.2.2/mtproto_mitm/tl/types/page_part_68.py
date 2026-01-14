from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8e3f9ebe, name="types.PagePart_68")
class PagePart_68(TLObject):
    blocks: list[TLObject] = TLField()
    photos: list[TLObject] = TLField()
    documents: list[TLObject] = TLField()
