from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc516d679, name="types.MessageActionBotAllowed")
class MessageActionBotAllowed(TLObject):
    flags: Int = TLField(is_flags=True)
    attach_menu: bool = TLField(flag=1 << 1)
    from_request: bool = TLField(flag=1 << 3)
    domain: Optional[str] = TLField(flag=1 << 0)
    app: Optional[TLObject] = TLField(flag=1 << 2)
