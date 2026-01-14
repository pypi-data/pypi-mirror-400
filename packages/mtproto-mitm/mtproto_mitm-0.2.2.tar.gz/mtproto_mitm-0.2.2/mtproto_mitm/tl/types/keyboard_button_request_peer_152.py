from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd0b468c, name="types.KeyboardButtonRequestPeer_152")
class KeyboardButtonRequestPeer_152(TLObject):
    text: str = TLField()
    button_id: Int = TLField()
    peer_type: TLObject = TLField()
