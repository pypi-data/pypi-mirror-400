from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1516d7bd, name="functions.account.SendConfirmPhoneCode_54")
class SendConfirmPhoneCode_54(TLObject):
    flags: Int = TLField(is_flags=True)
    allow_flashcall: bool = TLField(flag=1 << 0)
    hash: str = TLField()
    current_number: bool = TLField(flag=1 << 0, flag_serializable=True)
