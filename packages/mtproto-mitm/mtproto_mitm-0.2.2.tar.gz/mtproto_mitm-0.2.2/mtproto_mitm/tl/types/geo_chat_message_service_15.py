from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd34fa24e, name="types.GeoChatMessageService_15")
class GeoChatMessageService_15(TLObject):
    chat_id: Int = TLField()
    id: Int = TLField()
    from_id: Int = TLField()
    date: Int = TLField()
    action: TLObject = TLField()
