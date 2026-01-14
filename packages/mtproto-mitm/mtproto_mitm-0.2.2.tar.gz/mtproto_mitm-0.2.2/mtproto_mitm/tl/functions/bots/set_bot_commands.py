from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x517165a, name="functions.bots.SetBotCommands")
class SetBotCommands(TLObject):
    scope: TLObject = TLField()
    lang_code: str = TLField()
    commands: list[TLObject] = TLField()
