from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9e3cacb0, name="functions.messages.SearchGlobal_41")
class SearchGlobal_41(TLObject):
    q: str = TLField()
    offset_date: Int = TLField()
    offset_peer: TLObject = TLField()
    offset_id: Int = TLField()
    limit: Int = TLField()
