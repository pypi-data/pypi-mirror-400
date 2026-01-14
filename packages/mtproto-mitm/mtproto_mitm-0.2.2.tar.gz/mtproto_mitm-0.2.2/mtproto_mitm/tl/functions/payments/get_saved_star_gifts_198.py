from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x23830de9, name="functions.payments.GetSavedStarGifts_198")
class GetSavedStarGifts_198(TLObject):
    flags: Int = TLField(is_flags=True)
    exclude_unsaved: bool = TLField(flag=1 << 0)
    exclude_saved: bool = TLField(flag=1 << 1)
    exclude_unlimited: bool = TLField(flag=1 << 2)
    exclude_limited: bool = TLField(flag=1 << 3)
    exclude_unique: bool = TLField(flag=1 << 4)
    sort_by_value: bool = TLField(flag=1 << 5)
    peer: TLObject = TLField()
    offset: str = TLField()
    limit: Int = TLField()
