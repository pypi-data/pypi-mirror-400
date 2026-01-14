from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa6c4600c, name="functions.phone.RequestCall_196")
class RequestCall_196(TLObject):
    flags: Int = TLField(is_flags=True)
    video: bool = TLField(flag=1 << 0)
    user_id: TLObject = TLField()
    conference_call: Optional[TLObject] = TLField(flag=1 << 1)
    random_id: Int = TLField()
    g_a_hash: bytes = TLField()
    protocol: TLObject = TLField()
