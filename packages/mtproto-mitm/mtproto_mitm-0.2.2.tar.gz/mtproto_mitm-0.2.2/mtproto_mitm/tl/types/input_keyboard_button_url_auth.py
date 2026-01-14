from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd02e7fd4, name="types.InputKeyboardButtonUrlAuth")
class InputKeyboardButtonUrlAuth(TLObject):
    flags: Int = TLField(is_flags=True)
    request_write_access: bool = TLField(flag=1 << 0)
    text: str = TLField()
    fwd_text: Optional[str] = TLField(flag=1 << 1)
    url: str = TLField()
    bot: TLObject = TLField()
