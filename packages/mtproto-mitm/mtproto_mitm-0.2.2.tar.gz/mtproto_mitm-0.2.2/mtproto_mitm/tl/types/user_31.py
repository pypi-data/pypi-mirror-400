from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x22e49072, name="types.User_31")
class User_31(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    access_hash: Optional[Long] = TLField(flag=1 << 0)
    first_name: Optional[str] = TLField(flag=1 << 1)
    last_name: Optional[str] = TLField(flag=1 << 2)
    username: Optional[str] = TLField(flag=1 << 3)
    phone: Optional[str] = TLField(flag=1 << 4)
    photo: Optional[TLObject] = TLField(flag=1 << 5)
    status: Optional[TLObject] = TLField(flag=1 << 6)
    bot_info_version: Optional[Int] = TLField(flag=1 << 14)
