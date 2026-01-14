from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x98613ebf, name="types.Passkey")
class Passkey(TLObject):
    flags: Int = TLField(is_flags=True)
    id: str = TLField()
    name: str = TLField()
    date: Int = TLField()
    software_emoji_id: Optional[Long] = TLField(flag=1 << 0)
    last_usage_date: Optional[Int] = TLField(flag=1 << 1)
