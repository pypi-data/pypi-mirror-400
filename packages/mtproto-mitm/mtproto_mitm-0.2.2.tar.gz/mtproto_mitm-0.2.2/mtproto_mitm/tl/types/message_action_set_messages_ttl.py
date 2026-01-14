from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3c134d7b, name="types.MessageActionSetMessagesTTL")
class MessageActionSetMessagesTTL(TLObject):
    flags: Int = TLField(is_flags=True)
    period: Int = TLField()
    auto_setting_from: Optional[Long] = TLField(flag=1 << 0)
