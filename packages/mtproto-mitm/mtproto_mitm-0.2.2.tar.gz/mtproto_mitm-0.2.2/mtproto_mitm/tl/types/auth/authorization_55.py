from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcd050916, name="types.auth.Authorization_55")
class Authorization_55(TLObject):
    flags: Int = TLField(is_flags=True)
    tmp_sessions: Optional[Int] = TLField(flag=1 << 0)
    user: TLObject = TLField()
