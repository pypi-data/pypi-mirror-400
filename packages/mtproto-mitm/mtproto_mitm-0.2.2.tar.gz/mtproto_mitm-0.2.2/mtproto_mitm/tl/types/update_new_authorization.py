from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8951abef, name="types.UpdateNewAuthorization")
class UpdateNewAuthorization(TLObject):
    flags: Int = TLField(is_flags=True)
    unconfirmed: bool = TLField(flag=1 << 0)
    hash: Long = TLField()
    date: Optional[Int] = TLField(flag=1 << 0)
    device: Optional[str] = TLField(flag=1 << 0)
    location: Optional[str] = TLField(flag=1 << 0)
