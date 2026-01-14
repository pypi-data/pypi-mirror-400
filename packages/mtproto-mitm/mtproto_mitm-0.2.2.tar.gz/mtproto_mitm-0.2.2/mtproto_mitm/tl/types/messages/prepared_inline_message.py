from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xff57708d, name="types.messages.PreparedInlineMessage")
class PreparedInlineMessage(TLObject):
    query_id: Long = TLField()
    result: TLObject = TLField()
    peer_types: list[TLObject] = TLField()
    cache_time: Int = TLField()
    users: list[TLObject] = TLField()
