from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8a4f3c29, name="types.help.PremiumPromo_143")
class PremiumPromo_143(TLObject):
    status_text: str = TLField()
    status_entities: list[TLObject] = TLField()
    video_sections: list[str] = TLField()
    videos: list[TLObject] = TLField()
    currency: str = TLField()
    monthly_amount: Long = TLField()
    users: list[TLObject] = TLField()
