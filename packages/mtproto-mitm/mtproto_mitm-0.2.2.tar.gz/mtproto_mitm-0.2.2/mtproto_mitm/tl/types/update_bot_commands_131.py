from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcf7e0873, name="types.UpdateBotCommands_131")
class UpdateBotCommands_131(TLObject):
    peer: TLObject = TLField()
    bot_id: Int = TLField()
    commands: list[TLObject] = TLField()
