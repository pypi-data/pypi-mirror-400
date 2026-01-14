from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x770a8e74, name="functions.payments.ValidateRequestedInfo_65")
class ValidateRequestedInfo_65(TLObject):
    flags: Int = TLField(is_flags=True)
    save: bool = TLField(flag=1 << 0)
    msg_id: Int = TLField()
    info: TLObject = TLField()
