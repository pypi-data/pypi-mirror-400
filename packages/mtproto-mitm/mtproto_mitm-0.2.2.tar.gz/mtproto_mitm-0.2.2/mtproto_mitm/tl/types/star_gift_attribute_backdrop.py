from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd93d859c, name="types.StarGiftAttributeBackdrop")
class StarGiftAttributeBackdrop(TLObject):
    name: str = TLField()
    backdrop_id: Int = TLField()
    center_color: Int = TLField()
    edge_color: Int = TLField()
    pattern_color: Int = TLField()
    text_color: Int = TLField()
    rarity_permille: Int = TLField()
