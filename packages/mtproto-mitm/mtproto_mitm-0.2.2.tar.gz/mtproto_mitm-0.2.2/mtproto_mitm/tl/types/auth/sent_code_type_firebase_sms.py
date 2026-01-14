from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9fd736, name="types.auth.SentCodeTypeFirebaseSms")
class SentCodeTypeFirebaseSms(TLObject):
    flags: Int = TLField(is_flags=True)
    nonce: Optional[bytes] = TLField(flag=1 << 0)
    play_integrity_project_id: Optional[Long] = TLField(flag=1 << 2)
    play_integrity_nonce: Optional[bytes] = TLField(flag=1 << 2)
    receipt: Optional[str] = TLField(flag=1 << 1)
    push_timeout: Optional[Int] = TLField(flag=1 << 1)
    length: Int = TLField()
