from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xaf42ae29, name="types.MessageActionSuggestedPostApproval_206")
class MessageActionSuggestedPostApproval_206(TLObject):
    flags: Int = TLField(is_flags=True)
    rejected: bool = TLField(flag=1 << 0)
    balance_too_low: bool = TLField(flag=1 << 1)
    reject_comment: Optional[str] = TLField(flag=1 << 2)
    schedule_date: Optional[Int] = TLField(flag=1 << 3)
    stars_amount: Optional[Long] = TLField(flag=1 << 4)
