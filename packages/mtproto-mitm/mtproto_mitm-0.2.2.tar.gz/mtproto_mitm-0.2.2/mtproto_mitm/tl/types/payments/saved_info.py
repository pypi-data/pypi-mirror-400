from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfb8fe43c, name="types.payments.SavedInfo")
class SavedInfo(TLObject):
    flags: Int = TLField(is_flags=True)
    has_saved_credentials: bool = TLField(flag=1 << 1)
    saved_info: Optional[TLObject] = TLField(flag=1 << 0)
