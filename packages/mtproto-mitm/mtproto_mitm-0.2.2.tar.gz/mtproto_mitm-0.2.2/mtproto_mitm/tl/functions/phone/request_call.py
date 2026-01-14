from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x42ff96ed, name="functions.phone.RequestCall")
class RequestCall(TLObject):
    flags: Int = TLField(is_flags=True)
    video: bool = TLField(flag=1 << 0)
    user_id: TLObject = TLField()
    random_id: Int = TLField()
    g_a_hash: bytes = TLField()
    protocol: TLObject = TLField()
