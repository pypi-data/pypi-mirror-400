from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4d712f2e, name="types.UpdateBotCommands")
class UpdateBotCommands(TLObject):
    peer: TLObject = TLField()
    bot_id: Long = TLField()
    commands: list[TLObject] = TLField()
