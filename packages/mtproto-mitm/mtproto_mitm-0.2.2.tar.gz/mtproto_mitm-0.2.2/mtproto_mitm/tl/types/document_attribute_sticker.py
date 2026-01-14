from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6319d612, name="types.DocumentAttributeSticker")
class DocumentAttributeSticker(TLObject):
    flags: Int = TLField(is_flags=True)
    mask: bool = TLField(flag=1 << 1)
    alt: str = TLField()
    stickerset: TLObject = TLField()
    mask_coords: Optional[TLObject] = TLField(flag=1 << 0)
