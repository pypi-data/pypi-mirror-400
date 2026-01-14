from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe57b1432, name="types.auth.SentCodeTypeFirebaseSms_152")
class SentCodeTypeFirebaseSms_152(TLObject):
    flags: Int = TLField(is_flags=True)
    nonce: Optional[bytes] = TLField(flag=1 << 0)
    receipt: Optional[str] = TLField(flag=1 << 1)
    push_timeout: Optional[Int] = TLField(flag=1 << 1)
    length: Int = TLField()
