from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1f4a0e87, name="functions.payments.CreateStarGiftCollection")
class CreateStarGiftCollection(TLObject):
    peer: TLObject = TLField()
    title: str = TLField()
    stargift: list[TLObject] = TLField()
