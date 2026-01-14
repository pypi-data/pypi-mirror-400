from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x35bbdb6b, name="types.KeyboardButtonCallback")
class KeyboardButtonCallback(TLObject):
    flags: Int = TLField(is_flags=True)
    requires_password: bool = TLField(flag=1 << 0)
    text: str = TLField()
    data: bytes = TLField()
