from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xaa472651, name="types.DialogFilter")
class DialogFilter(TLObject):
    flags: Int = TLField(is_flags=True)
    contacts: bool = TLField(flag=1 << 0)
    non_contacts: bool = TLField(flag=1 << 1)
    groups: bool = TLField(flag=1 << 2)
    broadcasts: bool = TLField(flag=1 << 3)
    bots: bool = TLField(flag=1 << 4)
    exclude_muted: bool = TLField(flag=1 << 11)
    exclude_read: bool = TLField(flag=1 << 12)
    exclude_archived: bool = TLField(flag=1 << 13)
    title_noanimate: bool = TLField(flag=1 << 28)
    id: Int = TLField()
    title: TLObject = TLField()
    emoticon: Optional[str] = TLField(flag=1 << 25)
    color: Optional[Int] = TLField(flag=1 << 27)
    pinned_peers: list[TLObject] = TLField()
    include_peers: list[TLObject] = TLField()
    exclude_peers: list[TLObject] = TLField()
