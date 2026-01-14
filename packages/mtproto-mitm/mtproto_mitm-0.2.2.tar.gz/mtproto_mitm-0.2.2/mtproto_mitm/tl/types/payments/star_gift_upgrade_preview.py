from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3de1dfed, name="types.payments.StarGiftUpgradePreview")
class StarGiftUpgradePreview(TLObject):
    sample_attributes: list[TLObject] = TLField()
    prices: list[TLObject] = TLField()
    next_prices: list[TLObject] = TLField()
