from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x89464b50, name="functions.auth.RequestFirebaseSms_152")
class RequestFirebaseSms_152(TLObject):
    flags: Int = TLField(is_flags=True)
    phone_number: str = TLField()
    phone_code_hash: str = TLField()
    safety_net_token: Optional[str] = TLField(flag=1 << 0)
    ios_push_secret: Optional[str] = TLField(flag=1 << 1)
