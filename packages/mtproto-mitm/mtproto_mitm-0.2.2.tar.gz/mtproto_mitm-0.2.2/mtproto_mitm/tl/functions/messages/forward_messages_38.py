from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x708e0195, name="functions.messages.ForwardMessages_38")
class ForwardMessages_38(TLObject):
    flags: Int = TLField(is_flags=True)
    from_peer: TLObject = TLField()
    id: list[Int] = TLField()
    random_id: list[Long] = TLField()
    to_peer: TLObject = TLField()
