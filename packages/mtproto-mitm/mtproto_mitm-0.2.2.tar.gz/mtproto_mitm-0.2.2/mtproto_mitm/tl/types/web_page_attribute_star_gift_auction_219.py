from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x34986ab, name="types.WebPageAttributeStarGiftAuction_219")
class WebPageAttributeStarGiftAuction_219(TLObject):
    gift: TLObject = TLField()
    end_date: Int = TLField()
    center_color: Int = TLField()
    edge_color: Int = TLField()
    text_color: Int = TLField()
