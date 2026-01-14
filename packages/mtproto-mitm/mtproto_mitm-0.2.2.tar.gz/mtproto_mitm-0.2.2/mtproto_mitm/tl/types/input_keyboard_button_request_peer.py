from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc9662d05, name="types.InputKeyboardButtonRequestPeer")
class InputKeyboardButtonRequestPeer(TLObject):
    flags: Int = TLField(is_flags=True)
    name_requested: bool = TLField(flag=1 << 0)
    username_requested: bool = TLField(flag=1 << 1)
    photo_requested: bool = TLField(flag=1 << 2)
    text: str = TLField()
    button_id: Int = TLField()
    peer_type: TLObject = TLField()
    max_quantity: Int = TLField()
