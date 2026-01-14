from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbdedf566, name="types.SponsoredMessage_179")
class SponsoredMessage_179(TLObject):
    flags: Int = TLField(is_flags=True)
    recommended: bool = TLField(flag=1 << 5)
    can_report: bool = TLField(flag=1 << 12)
    random_id: bytes = TLField()
    url: str = TLField()
    title: str = TLField()
    message: str = TLField()
    entities: Optional[list[TLObject]] = TLField(flag=1 << 1)
    photo: Optional[TLObject] = TLField(flag=1 << 6)
    color: Optional[TLObject] = TLField(flag=1 << 13)
    button_text: str = TLField()
    sponsor_info: Optional[str] = TLField(flag=1 << 7)
    additional_info: Optional[str] = TLField(flag=1 << 8)
