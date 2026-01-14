from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb0cd6617, name="types.BotVerifierSettings")
class BotVerifierSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    can_modify_custom_description: bool = TLField(flag=1 << 1)
    icon: Long = TLField()
    company: str = TLField()
    custom_description: Optional[str] = TLField(flag=1 << 0)
