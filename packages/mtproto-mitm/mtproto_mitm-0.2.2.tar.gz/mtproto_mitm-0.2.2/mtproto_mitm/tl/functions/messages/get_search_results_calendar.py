from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6aa3f6bd, name="functions.messages.GetSearchResultsCalendar")
class GetSearchResultsCalendar(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    saved_peer_id: Optional[TLObject] = TLField(flag=1 << 2)
    filter: TLObject = TLField()
    offset_id: Int = TLField()
    offset_date: Int = TLField()
