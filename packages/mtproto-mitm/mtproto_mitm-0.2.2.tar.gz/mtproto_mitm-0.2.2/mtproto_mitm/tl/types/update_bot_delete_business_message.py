from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa02a982e, name="types.UpdateBotDeleteBusinessMessage")
class UpdateBotDeleteBusinessMessage(TLObject):
    connection_id: str = TLField()
    peer: TLObject = TLField()
    messages: list[Int] = TLField()
    qts: Int = TLField()
