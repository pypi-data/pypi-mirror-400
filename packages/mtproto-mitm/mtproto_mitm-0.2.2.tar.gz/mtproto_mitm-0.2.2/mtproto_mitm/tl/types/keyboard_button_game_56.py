from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x28fc3164, name="types.KeyboardButtonGame_56")
class KeyboardButtonGame_56(TLObject):
    text: str = TLField()
    game_title: str = TLField()
    game_id: Int = TLField()
    start_param: str = TLField()
