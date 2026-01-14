from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x26fb7289, name="functions.messages.GetChatInviteImporters_124")
class GetChatInviteImporters_124(TLObject):
    peer: TLObject = TLField()
    link: str = TLField()
    offset_date: Int = TLField()
    offset_user: TLObject = TLField()
    limit: Int = TLField()
