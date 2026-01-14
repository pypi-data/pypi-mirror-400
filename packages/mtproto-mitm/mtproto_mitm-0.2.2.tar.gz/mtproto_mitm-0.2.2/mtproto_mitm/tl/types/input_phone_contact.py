from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6a1dc4be, name="types.InputPhoneContact")
class InputPhoneContact(TLObject):
    flags: Int = TLField(is_flags=True)
    client_id: Long = TLField()
    phone: str = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    note: Optional[TLObject] = TLField(flag=1 << 0)
