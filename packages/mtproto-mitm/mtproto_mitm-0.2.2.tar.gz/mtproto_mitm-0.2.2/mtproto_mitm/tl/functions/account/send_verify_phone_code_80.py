from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x823380b4, name="functions.account.SendVerifyPhoneCode_80")
class SendVerifyPhoneCode_80(TLObject):
    flags: Int = TLField(is_flags=True)
    allow_flashcall: bool = TLField(flag=1 << 0)
    phone_number: str = TLField()
    current_number: bool = TLField(flag=1 << 0, flag_serializable=True)
