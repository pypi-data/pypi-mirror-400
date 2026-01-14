from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa319e569, name="functions.payments.GetSavedStarGifts")
class GetSavedStarGifts(TLObject):
    flags: Int = TLField(is_flags=True)
    exclude_unsaved: bool = TLField(flag=1 << 0)
    exclude_saved: bool = TLField(flag=1 << 1)
    exclude_unlimited: bool = TLField(flag=1 << 2)
    exclude_unique: bool = TLField(flag=1 << 4)
    sort_by_value: bool = TLField(flag=1 << 5)
    exclude_upgradable: bool = TLField(flag=1 << 7)
    exclude_unupgradable: bool = TLField(flag=1 << 8)
    peer_color_available: bool = TLField(flag=1 << 9)
    exclude_hosted: bool = TLField(flag=1 << 10)
    peer: TLObject = TLField()
    collection_id: Optional[Int] = TLField(flag=1 << 6)
    offset: str = TLField()
    limit: Int = TLField()
