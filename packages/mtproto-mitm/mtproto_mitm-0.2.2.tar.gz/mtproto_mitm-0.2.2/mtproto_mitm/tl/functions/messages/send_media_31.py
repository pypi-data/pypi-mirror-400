from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc8f16791, name="functions.messages.SendMedia_31")
class SendMedia_31(TLObject):
    flags: Int = TLField(is_flags=True)
    peer: TLObject = TLField()
    reply_to_msg_id: Optional[Int] = TLField(flag=1 << 0)
    media: TLObject = TLField()
    random_id: Long = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
