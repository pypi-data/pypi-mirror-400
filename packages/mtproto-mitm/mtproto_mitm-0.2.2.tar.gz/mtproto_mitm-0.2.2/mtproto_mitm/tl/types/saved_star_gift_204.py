from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdfda0499, name="types.SavedStarGift_204")
class SavedStarGift_204(TLObject):
    flags: Int = TLField(is_flags=True)
    name_hidden: bool = TLField(flag=1 << 0)
    unsaved: bool = TLField(flag=1 << 5)
    refunded: bool = TLField(flag=1 << 9)
    can_upgrade: bool = TLField(flag=1 << 10)
    pinned_to_top: bool = TLField(flag=1 << 12)
    from_id: Optional[TLObject] = TLField(flag=1 << 1)
    date: Int = TLField()
    gift: TLObject = TLField()
    message: Optional[TLObject] = TLField(flag=1 << 2)
    msg_id: Optional[Int] = TLField(flag=1 << 3)
    saved_id: Optional[Long] = TLField(flag=1 << 11)
    convert_stars: Optional[Long] = TLField(flag=1 << 4)
    upgrade_stars: Optional[Long] = TLField(flag=1 << 6)
    can_export_at: Optional[Int] = TLField(flag=1 << 7)
    transfer_stars: Optional[Long] = TLField(flag=1 << 8)
    can_transfer_at: Optional[Int] = TLField(flag=1 << 13)
    can_resell_at: Optional[Int] = TLField(flag=1 << 14)
