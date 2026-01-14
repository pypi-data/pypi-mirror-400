from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf897d33e, name="types.BotInlineMediaResultDocument_45")
class BotInlineMediaResultDocument_45(TLObject):
    id: str = TLField()
    type_: str = TLField()
    document: TLObject = TLField()
    send_message: TLObject = TLField()
