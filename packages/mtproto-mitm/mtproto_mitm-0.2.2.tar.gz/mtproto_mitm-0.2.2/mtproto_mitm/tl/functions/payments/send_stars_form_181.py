from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2bb731d, name="functions.payments.SendStarsForm_181")
class SendStarsForm_181(TLObject):
    flags: Int = TLField(is_flags=True)
    form_id: Long = TLField()
    invoice: TLObject = TLField()
