from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8b89dfbd, name="functions.bots.SetCustomVerification")
class SetCustomVerification(TLObject):
    flags: Int = TLField(is_flags=True)
    enabled: bool = TLField(flag=1 << 1)
    bot: Optional[TLObject] = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    custom_description: Optional[str] = TLField(flag=1 << 2)
